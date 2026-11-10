"""Dựng trang web sơ đồ cây của Phòng R&D (một file HTML tự chứa) và phục vụ qua HTTP local.

  python3 dtlab.py site    → web/dist/index.html
  python3 dtlab.py serve   → dựng rồi mở http://localhost:8766
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

import yaml

from . import site_content as C

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web" / "template.html"
DIST = ROOT / "web" / "dist"


# ------------------------------------------------------------ markdown → html (đủ dùng cho báo cáo)
def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    # URL trần → link bấm được (bỏ qua URL đã nằm trong thẻ <a>)
    s = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<>"]+[^\s<>".,;:)])',
               r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
    return s


def md_to_html(md: str) -> str:
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><tr>" + "".join(f"<th>{_inline(h)}</th>" for h in head) + "</tr>"
                       + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
                       + "</table>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m:
            tag = "h2" if len(m.group(1)) <= 2 else "h4"
            out.append(f"<{tag}>{_inline(m.group(2))}</{tag}>")
            i += 1
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.", ln))
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                t = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                t = re.sub(r"^\[( |x)\]\s*", lambda mm: "☑ " if mm.group(1) == "x" else "☐ ", t)
                items.append(f"<li>{_inline(t)}</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        if ln.lstrip().startswith(">"):
            q = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                q.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(q))}</blockquote>")
            continue
        if ln.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
            continue
        para = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|>|\||\s*[-*]\s|\s*\d+\.\s|```)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")
    return "\n".join(out)


def _slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.encode("ascii", "ignore").decode()).strip("-").lower()
    return s[:48] or "muc"


def report_nodes(reports_dir: Path) -> list[dict]:
    """Mỗi file .md trong reports/ → 1 nút; mỗi mục '## ' → 1 nút con."""
    nodes = []
    for f in sorted(reports_dir.rglob("*.md"), reverse=True):
        text = f.read_text(encoding="utf-8", errors="ignore")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), f.stem)
        parts = re.split(r"^## ", text, flags=re.M)
        intro = re.sub(r"^# .*\n?", "", parts[0], count=1, flags=re.M)
        base = "r-" + _slug(f"{f.parent.name}-{f.stem}")
        kids = []
        for j, p in enumerate(parts[1:], 1):
            head, _, body = p.partition("\n")
            kids.append(C.N(f"{base}-{j}", head.strip(), "section", None, md_to_html(body)))
        nodes.append(C.N(base, f"{f.parent.name} · {title}", "report", "director",
                         md_to_html(intro) + f"<p class='muted'>Tệp: <code>{f.relative_to(reports_dir.parent)}</code></p>",
                         children=kids))
    return nodes


def team_nodes(team_cfg: dict) -> list[dict]:
    out = []
    for p in C.TEAM:
        spec = team_cfg["director"] if p["key"] == "director" else team_cfg["members"].get(p["key"], {})
        refs = ", ".join(spec.get("references", [])) if spec.get("references") else "CIGRE TB 995"
        scope = spec.get("scope") or spec.get("mission", "")
        qs = "".join(f"<li>{html.escape(q)}</li>" for q in spec.get("standing_questions", []))
        body = (f"<dl><dt>Vai trò</dt><dd>{html.escape(p['role'])}</dd><dt>Phạm vi</dt><dd>{html.escape(scope.strip())}</dd>"
                f"<dt>Tiêu chuẩn / tài liệu nền</dt><dd>{html.escape(refs)}</dd>"
                f"<dt>Đang làm</dt><dd>{html.escape(p['task'])}</dd></dl>"
                + (f"<h4>Câu hỏi thường trực</h4><ul>{qs}</ul>" if qs else ""))
        out.append(C.N(f"ns-{p['key']}", f"{p['name']} · {p['role']}", "person", p["key"], body))
    return out


def build_tree() -> dict:
    team_cfg = yaml.safe_load((ROOT / "config" / "team.yaml").read_text(encoding="utf-8"))
    auto = report_nodes(ROOT / "reports")
    root = C.N("goc", "Phòng R&D Digital Twin ngành điện", "root", "director", """
<p>Bản đồ tri thức của phòng. Bấm vào một nút để đọc chi tiết; bấm nút <b>+ / −</b> để mở hoặc thu gọn nhánh. Nhánh <i>Báo cáo trong kho</i> được dựng tự động từ thư mục <code>reports/</code>.</p>""",
        children=[C.report1, C.plan,
                  C.N("kho-bao-cao", "Báo cáo trong kho (tự động)", "group", "director",
                      "<p>Các báo cáo tuần do Qwen local và Claude tạo ra, đọc từ <code>reports/</code>.</p>", children=auto),
                  C.N("nhan-su", "Nhân sự phòng (8 agent)", "group", "director",
                      "<p>Mỗi chuyên viên là một AI agent có vai trò, tiêu chuẩn và câu hỏi thường trực riêng (sửa trong <code>config/team.yaml</code>).</p>",
                      children=team_nodes(team_cfg)),
                  C.tools])
    return root


def build(out_dir: Path = DIST) -> Path:
    data = {"tree": build_tree(), "team": C.TEAM,
            "built": dt.datetime.now().strftime("%d/%m/%Y %H:%M")}
    page = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DT_DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "index.html"
    path.write_text(page, encoding="utf-8")
    return path


def serve(port: int = 8766, open_browser: bool = True):
    import functools
    import http.server
    import webbrowser
    p = build()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(p.parent))
    url = f"http://localhost:{port}/"
    print(f"Trang sơ đồ cây: {url}  (Ctrl+C để dừng)")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        httpd.serve_forever()


# ------------------------------------------------------------------ trang đọc trên điện thoại
READER_CSS = """
:root{--bg:#F5F6FB;--card:#fff;--ink:#1E1B3A;--muted:#6B6B85;--line:#E7E7F1;--p:#5B4BF5;--soft:#EEEBFF;
--grad:linear-gradient(135deg,#5B4BF5,#8B5CF6 55%,#EC4899)}
@media (prefers-color-scheme:dark){:root{--bg:#14121f;--card:#1e1b2e;--ink:#ECEAF6;--muted:#a5a2bb;--line:#2e2a44;--soft:#2a2547}}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{position:sticky;top:0;z-index:5;background:var(--grad);color:#fff;padding:14px 16px 10px}
header h1{margin:0;font-size:19px}header p{margin:2px 0 8px;font-size:12.5px;opacity:.9}
.tabs{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}
.tabs button{flex:none;border:0;border-radius:999px;padding:6px 12px;font-family:inherit;font-weight:600;font-size:13px;background:rgba(255,255,255,.22);color:#fff}
.tabs button.on{background:#fff;color:#5B4BF5}
main{padding:12px;max-width:820px;margin:0 auto}
input{width:100%;padding:10px 12px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-size:15px;margin-bottom:10px}
.item{background:var(--card);border:1px solid var(--line);border-radius:16px;margin-bottom:10px;overflow:hidden}
.item>button{width:100%;text-align:left;border:0;background:none;color:var(--ink);padding:14px;font-family:inherit;font-weight:600;font-size:15px;line-height:1.4;display:flex;gap:8px;align-items:flex-start}
.item>button small{display:block;font-weight:400;color:var(--muted);font-size:12px}
.item>button .chev{margin-left:auto;transition:transform .2s}.item.open>button .chev{transform:rotate(90deg)}
.body{display:none;padding:0 14px 14px;border-top:1px solid var(--line)}.item.open .body{display:block}
.body h4{font-size:16.5px;margin:18px 0 6px;color:var(--p)}
.body table{border-collapse:collapse;display:block;overflow-x:auto;font-size:13px;margin:8px 0}
.body th,.body td{border:1px solid var(--line);padding:5px 7px;vertical-align:top;min-width:70px}.body th{background:var(--soft)}
.body code{background:var(--soft);padding:0 4px;border-radius:5px;font-size:13px}.body a{color:var(--p);word-break:break-all}
.body ul,.body ol{padding-left:20px}.pill{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--soft);color:var(--p);flex:none}
mark{background:#FEF08A;color:#111}
"""


def _collect_docs():
    reps = []
    for f in sorted((ROOT / "reports").rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), f.stem)
        body = re.sub(r"^# .*\n?", "", text, count=1, flags=re.M).replace("\n## ", "\n### ")
        reps.append({"title": title, "sub": f.parent.name, "html": md_to_html("\n" + body)})
    facts = []
    for f in sorted((ROOT / "library").rglob("FS*.md")):
        text = f.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), f.stem)
        body = re.sub(r"^# .*\n?", "", text, count=1, flags=re.M).replace("\n## ", "\n### ")
        facts.append({"title": title, "sub": f.parent.name, "html": md_to_html("\n" + body)})
    return list(reversed(reps)), facts


def build_reader(out_dir: Path = DIST) -> Path:
    """Trang tĩnh gọn cho điện thoại: tất cả báo cáo + fact sheet, tìm kiếm, mở/đóng từng mục."""
    reps, facts = _collect_docs()
    data = json.dumps({"reports": reps, "facts": facts}, ensure_ascii=False).replace("</", "<\\/")
    page = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>DT-RnD-Lab – Báo cáo</title>
<style>{READER_CSS}</style></head><body>
<header><h1>⚡ DT-RnD-Lab · Phòng R&amp;D Digital Twin</h1>
<p>Bản đọc trên điện thoại · cập nhật {dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).strftime('%d/%m/%Y %H:%M')}</p>
<div class="tabs"><button data-t="reports" class="on">📑 Báo cáo</button><button data-t="facts">📚 Kho tri thức</button></div></header>
<main><input id="q" placeholder="Tìm: TB 995, DGA, 110 kV, Hitachi…" type="search"><div id="list"></div></main>
<script>
const D={data};let tab="reports";
const esc=s=>s.replace(/[&<>]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;"}}[c]));
function render(){{const q=document.getElementById("q").value.trim().toLowerCase();const L=document.getElementById("list");L.innerHTML="";
D[tab].forEach((d,i)=>{{const txt=(d.title+" "+d.html.replace(/<[^>]+>/g," ")).toLowerCase();if(q&&!txt.includes(q))return;
const it=document.createElement("div");it.className="item"+(q?" open":"");
it.innerHTML=`<button><span>${{esc(d.title)}}<small>${{esc(d.sub)}}</small></span><span class="chev">›</span></button><div class="body">${{d.html}}</div>`;
it.querySelector("button").onclick=()=>it.classList.toggle("open");L.appendChild(it);}});
if(!L.children.length)L.innerHTML='<p style="color:var(--muted)">Không tìm thấy.</p>';}}
document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>{{tab=b.dataset.t;document.querySelectorAll(".tabs button").forEach(x=>x.classList.toggle("on",x===b));render();}});
document.getElementById("q").oninput=render;render();
</script></body></html>"""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "reader.html"
    path.write_text(page, encoding="utf-8")
    return path
