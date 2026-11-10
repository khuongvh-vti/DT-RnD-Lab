"""Dựng trang web sơ đồ cây của Phòng R&D (một file HTML tự chứa) và phục vụ qua HTTP local.

  python3 dtlab.py site    → web/dist/index.html
  python3 dtlab.py serve   → dựng rồi mở http://localhost:8765
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
        m = re.match(r"^(#{3,6})\s+(.*)", ln)
        if m:
            out.append(f"<h4>{_inline(m.group(2))}</h4>")
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
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*[-*]\s|\s*\d+\.\s|```)", lines[i]):
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


def serve(port: int = 8765, open_browser: bool = True):
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
