"""VTI R&D Lab (repo DT-RnD-Lab) – ứng dụng web local (mở bằng Chrome). Chạy: python3 app/server.py → http://localhost:8766
Chỉ dùng thư viện chuẩn Python + các module trong lab/. Việc nặng (hỏi Qwen, vòng tuần, nạp tài liệu) chạy nền theo job."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import threading
import traceback
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from lab import docx_export, news, site  # noqa: E402
from lab import modules as M  # noqa: E402
from lab import site_content as C  # noqa: E402
from lab.physics import dga, scl, transformer_thermal as th  # noqa: E402

PORT = int(os.environ.get("DT_PORT", "8766"))
REMOTE_CFG = Path(__file__).resolve().parents[1] / "data" / "remote.json"  # bật truy cập từ điện thoại (scripts/enable_phone.sh)


def remote_cfg() -> dict:
    try:
        return json.loads(REMOTE_CFG.read_text(encoding="utf-8"))
    except Exception:
        return {}
STATIC = ROOT / "app" / "static"
DATA = ROOT / "data"
LIB = ROOT / "library"
REPORTS = ROOT / "reports"
CHAT = DATA / "chat.json"
MAX_BODY = 60 * 1024 * 1024
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml", ".png": "image/png"}
PHASES = [  # lộ trình nghiên cứu
    ("GĐ1", "Nền tảng tri thức", "2026-11-11", "2026-12-20"),
    ("GĐ2", "Mổ xẻ thị trường", "2026-12-07", "2027-01-24"),
    ("GĐ3", "Làm chủ mô hình", "2027-01-25", "2027-04-18"),
    ("GĐ4", "Định hình sản phẩm & hồ sơ", "2027-04-19", "2027-05-30"),
    ("GĐ5", "Pilot", "2027-06-01", "2027-12-31"),
]

JOBS: dict[str, dict] = {}
_LLM = None


# ------------------------------------------------------------------ helpers
def load_cfg():
    s = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    t = yaml.safe_load((ROOT / "config/team.yaml").read_text(encoding="utf-8"))
    for k in ("library", "index_db", "reports"):
        s["paths"][k] = str(ROOT / s["paths"][k])
    return s, t


def get_llm(s):
    global _LLM
    if _LLM is None:
        from lab.cloud import HybridLLM
        from lab.hardware import recommend_model
        from lab.llm import OllamaClient
        o = s["ollama"]
        model = recommend_model()[0] if o["chat_model"] == "auto" else o["chat_model"]
        local = OllamaClient(o["host"], model, o["embed_model"], o["temperature"], o["num_ctx"], o["timeout_s"])
        _LLM = HybridLLM(local, s.get("cloud", {}), str(DATA), log=lambda *_: None)
    return _LLM


def director(s, t):
    from lab.knowledge import KnowledgeBase
    from lab.team import Director
    llm = get_llm(s)
    kb = KnowledgeBase(s["paths"]["index_db"], llm, s["rag"]["chunk_chars"], s["rag"]["overlap_chars"])
    return Director(t, s, llm, kb), kb


def start_job(kind: str, fn, *args):
    jid = uuid.uuid4().hex[:10]
    JOBS[jid] = {"id": jid, "kind": kind, "state": "running", "log": [], "result": None,
                 "started": dt.datetime.now().isoformat(timespec="seconds")}

    def log(*a):
        JOBS[jid]["log"].append(" ".join(str(x) for x in a))

    def run():
        try:
            JOBS[jid]["result"] = fn(log, *args)
            JOBS[jid]["state"] = "done"
        except Exception as e:  # pragma: no cover - lỗi runtime hiển thị cho người dùng
            JOBS[jid]["state"] = "error"
            msg = f"{type(e).__name__}: {e}"
            if "Connection refused" in msg or "URLError" in msg or "LLMError" in msg:
                msg = "Không kết nối được Ollama (Qwen local). Mở app Ollama rồi thử lại. Chi tiết: " + msg
            JOBS[jid]["result"] = msg
            log(traceback.format_exc(limit=3))
    threading.Thread(target=run, daemon=True).start()
    return jid


def phase_now(today=None, mid: str = "dt"):
    mod = M.load().get(mid)
    if mod and mod.get("phases"):
        return M.phase_now(mod, today)
    today = today or dt.date.today().isoformat()
    cur = next((p for p in PHASES if p[2] <= today <= p[3]), None)
    if cur is None:
        cur = PHASES[0] if today < PHASES[0][2] else PHASES[-1]
    a, b = dt.date.fromisoformat(cur[2]), dt.date.fromisoformat(cur[3])
    t = dt.date.fromisoformat(today)
    pct = max(0.0, min(1.0, (t - a).days / max(1, (b - a).days)))
    return {"code": cur[0], "name": cur[1], "start": cur[2], "end": cur[3], "pct": round(pct, 3),
            "days_left": max(0, (b - t).days), "all": [dict(zip(("code", "name", "start", "end"), p)) for p in PHASES]}


def list_reports():
    out = []
    for f in sorted(REPORTS.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        text = f.read_text(encoding="utf-8", errors="ignore")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), f.stem)
        out.append({"path": str(f.relative_to(ROOT)), "week": f.parent.name, "title": title,
                    "mtime": dt.datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y %H:%M")})
    return out


def safe_path(rel: str, base: Path) -> Path:
    p = (ROOT / rel).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        raise ValueError("path")
    return p


def docx_name(*parts: str) -> str:
    return "_".join(re.sub(r"[\\/:*?\"<>|\s]+", "_", x).strip("_") for x in parts if x) + ".docx"


def team_list() -> list[dict]:
    """Trưởng phòng + khối dùng chung + chuyên viên riêng của mọi module (kèm ngoại hình để vẽ)."""
    _, t = load_cfg()
    mods = M.load()
    base = {p["key"]: p for p in C.TEAM}
    d = t["director"]
    out = [{**base["director"], "role": "Trưởng phòng – Điều phối mọi module", "title": d["name"], "scope": d["mission"].strip(),
            "references": [], "questions": [], "module": "director", "module_name": "Ban điều phối"}]
    ros = M.roster(t, mods)
    looks = M.personas(list(ros), base)
    for k, v in ros.items():
        p = looks[k]
        mod = mods.get(v["module"], {})
        out.append({**p, "role": v["name"].replace("Chuyên viên ", ""), "title": v["name"], "scope": v.get("scope", ""),
                    "task": p.get("task") or (v.get("standing_questions") or [""])[0],
                    "references": v.get("references", []), "questions": v.get("standing_questions", []),
                    "module": v["module"], "module_name": v["module_name"], "module_icon": mod.get("icon", "🤝"),
                    "module_status": mod.get("status", "active") if v["module"] != "shared" else "active"})
    return out


def modules_list() -> list[dict]:
    _, t = load_cfg()
    out = []
    for mid, m in M.load().items():
        docs = sum(1 for f in (x for d in (m.get("library") or []) if (LIB / d).is_dir() for x in (LIB / d).rglob("*"))
                   if f.is_file() and f.suffix.lower() in {".pdf", ".md", ".txt"} and f.name != "README.md")
        own = list((m.get("members") or {}).keys())
        out.append({"id": mid, **{k: m.get(k) for k in ("name", "icon", "status", "goal", "scope", "created", "library",
                                                          "questions", "keywords", "shared")},
                    "status_vi": M.STATUS_VI.get(m.get("status", "active")), "phase": M.phase_now(m),
                    "members": own, "member_names": [m["members"][k]["name"] for k in own], "docs": docs})
    return out


def chat_md(it: dict) -> str:
    who = {p["key"]: f"{p['name']} – {p['role']}" for p in team_list()}.get(it.get("agent") or "director", it.get("agent"))
    return (f"## Câu hỏi ({it.get('time', '')})\n\n> {it['q']}\n\n"
            f"### Trả lời của {who} · engine: {it.get('engine', 'local')}\n\n{it['a']}\n\n---")


def chat_history():
    try:
        return json.loads(CHAT.read_text(encoding="utf-8"))
    except Exception:
        return []


def chat_append(item):
    h = chat_history()[-199:] + [item]
    DATA.mkdir(exist_ok=True)
    CHAT.write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")


# ------------------------------------------------------------------ jobs
def job_ask(log, question, agent, module=None):
    s, t = load_cfg()
    boss, _ = director(s, t)
    log(f"Câu hỏi gửi tới: {agent or 'Trưởng phòng định tuyến'}{' · module ' + module if module else ''}")
    answer = boss.ask(question, members=[agent] if agent else None, module=module)
    engine = getattr(boss.llm, "last_engine", "local")
    item = {"time": dt.datetime.now().strftime("%d/%m %H:%M"), "agent": agent or "director", "q": question,
            "a": answer, "a_html": site.md_to_html(answer), "engine": engine, "module": module or ""}
    chat_append(item)
    return item


def last_cycle_time() -> float:
    files = list((REPORTS / "cycles").glob("*/BAO_CAO_3_NGAY.md")) if (REPORTS / "cycles").exists() else []
    return max((f.stat().st_mtime for f in files), default=0.0)


def new_docs_since(ts: float) -> list[str]:
    return sorted(str(f.relative_to(LIB)) for f in LIB.rglob("*")
                  if f.is_file() and f.suffix.lower() in {".pdf", ".md", ".txt"} and f.name != "README.md" and f.stat().st_mtime > ts)


def news_highlights(n: int = 8) -> str:
    lines = []
    for day in news_days()[:3]:
        d = news_load(day) or {}
        for x in [i for i in d.get("items", []) if i.get("is_opportunity")][:n]:
            lines.append(f"- [{day}] {x['title']} ({x.get('publisher', '')}) {x.get('link', '')}")
    return "\n".join(lines[:n])


def job_cycle(log, focus, mods=None):
    s, t = load_cfg()
    boss, kb = director(s, t)
    docs = new_docs_since(last_cycle_time())
    log(f"Nạp tài liệu mới vào kho… ({len(docs)} file mới kể từ chu kỳ trước)")
    kb.ingest(s["paths"]["library"], log=log)
    path = boss.run_cycle(focus, modules=mods or None, log=log, new_docs=docs, highlights=news_highlights())
    return {"path": str(Path(path).relative_to(ROOT))}


def cycle_cfg() -> dict:
    s, _ = load_cfg()
    return {"auto": True, "every_days": 3, "time": "07:00", **(s.get("cycle") or {})}


def cycle_due(now: dt.datetime | None = None) -> bool:
    """Đến hạn chu kỳ báo cáo khi đã qua giờ hẹn và chu kỳ trước cách ≥ every_days ngày (tính theo ngày)."""
    c = cycle_cfg()
    now = now or dt.datetime.now()
    if not c["auto"] or now.strftime("%H:%M") < str(c["time"]):
        return False
    last = last_cycle_time()
    if not last:
        return True
    return (now.date() - dt.datetime.fromtimestamp(last).date()).days >= int(c["every_days"])


def _code_mtime() -> float:
    files = [ROOT / "app" / "server.py", *(ROOT / "lab").rglob("*.py")]
    return max((f.stat().st_mtime for f in files if f.exists()), default=0.0)


CODE_MTIME = _code_mtime()


def code_watcher():
    """Tự khởi động lại server khi code Python thay đổi (sau khi đồng bộ bản mới) – chờ job đang chạy xong."""
    import time
    while True:
        time.sleep(5)
        try:
            if _code_mtime() > CODE_MTIME + 1 and not any(j["state"] == "running" for j in JOBS.values()):
                time.sleep(2)  # đợi giải nén xong
                print("Code thay đổi → khởi động lại server", file=sys.stderr, flush=True)
                os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            pass


def cycle_scheduler():
    import time
    while True:
        try:
            busy = any(j["kind"] == "cycle" and j["state"] == "running" for j in JOBS.values())
            if not busy and cycle_due() and get_llm(load_cfg()[0]).list_models():
                start_job("cycle", job_cycle, "", [])
        except Exception:
            pass
        time.sleep(300)


def job_week(log, focus):  # tương thích nút cũ
    return job_cycle(log, focus)


def job_new_module(log, form):
    s, t = load_cfg()
    llm = None
    try:
        llm = get_llm(s)
        if not llm.list_models() and not getattr(llm, "cloud", None):
            llm = None
    except Exception:
        llm = None
    mid = M.create(form, t, llm=llm, log=log)
    return {"id": mid, "intro": f"reports/modules/{mid}/00_GIOI_THIEU_MODULE.md"}


NEWS_DIR = DATA / "news"


def news_cfg() -> dict:
    return yaml.safe_load((ROOT / "config/news.yaml").read_text(encoding="utf-8"))


def news_days() -> list[str]:
    return sorted((f.stem for f in NEWS_DIR.glob("*.json")), reverse=True) if NEWS_DIR.exists() else []


def news_load(day: str | None = None) -> dict | None:
    days = news_days()
    day = day or (days[0] if days else None)
    if not day or not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
        return None
    f = NEWS_DIR / f"{day}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def job_news(log, with_ai=True):
    cfg = news_cfg()
    log("Đang lấy tin từ các nguồn…")
    d = news.collect(cfg, log=log)
    news.save(d, NEWS_DIR, int(cfg.get("keep_days", 60)))
    log(f"Đã lưu {len(d['items'])} tin, {sum(1 for x in d['items'] if x['is_opportunity'])} cơ hội.")
    if with_ai:
        try:
            s, _ = load_cfg()
            news.ai_enrich(d, get_llm(s), int(cfg.get("ai_top", 8)), log=log)
            news.save(d, NEWS_DIR, int(cfg.get("keep_days", 60)))
        except Exception as e:
            log(f"Bỏ qua phần AI (Ollama chưa chạy?): {e}")
    return {"date": d["date"], "items": len(d["items"])}


def news_scheduler():
    """Mỗi phút kiểm tra: tới giờ trong config (mặc định 06:30) mà chưa có bản tin hôm nay thì tự cập nhật."""
    import time
    while True:
        try:
            hhmm = str(news_cfg().get("schedule", "06:30"))
            now = dt.datetime.now()
            today = now.date().isoformat()
            running = any(j["kind"] == "news" and j["state"] == "running" for j in JOBS.values())
            if now.strftime("%H:%M") >= hhmm and today not in news_days() and not running:
                start_job("news", job_news, True)
        except Exception:
            pass
        time.sleep(60)


def job_ingest(log):
    s, t = load_cfg()
    _, kb = director(s, t)
    n = kb.ingest(s["paths"]["library"], log=log)
    return {"added": n, "stats": kb.stats()}


# ------------------------------------------------------------------ HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "DT-RnD-Lab/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body: bytes, ctype: str):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_docx(self, data: bytes, filename: str):
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        ascii_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", filename.encode("ascii", "ignore").decode()) or "bao_cao.docx"
        self.send_header("Content-Disposition",
                         f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{urllib.parse.quote(filename)}")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self) -> bytes:
        n = int(self.headers.get("Content-Length", 0) or 0)
        if n > MAX_BODY:
            raise ValueError("too_large")
        return self.rfile.read(n) if n else b""

    def jbody(self) -> dict:
        b = self.body()
        return json.loads(b.decode("utf-8")) if b else {}

    # ---------------- bảo vệ khi mở cho điện thoại: máy khác phải có mã truy cập
    def authorized(self, u) -> bool:
        if self.client_address[0] in ("127.0.0.1", "::1"):
            return True
        token = remote_cfg().get("token")
        if not token:
            return False
        q = dict(urllib.parse.parse_qsl(u.query))
        cookie = self.headers.get("Cookie", "")
        if q.get("key") == token:
            self._set_cookie = f"dtkey={token}; Path=/; Max-Age=31536000; SameSite=Strict; HttpOnly"
            return True
        return f"dtkey={token}" in cookie

    def deny(self):
        body = ("<html><meta name=viewport content='width=device-width'><body style='font-family:sans-serif;padding:24px'>"
                "<h3>DT-RnD-Lab</h3><p>Cần mã truy cập. Mở đúng đường link có <code>?key=…</code> "
                "mà lệnh <code>bash scripts/enable_phone.sh</code> in ra trên máy Mac.</p></body></html>").encode()
        self.send_response(401)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        c = getattr(self, "_set_cookie", None)
        if c:
            self.send_header("Set-Cookie", c)
            self._set_cookie = None
        super().end_headers()

    # ---------------- GET
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if not self.authorized(u):
            return self.deny()
        q = dict(urllib.parse.parse_qsl(u.query))
        try:
            if u.path in ("/", "/index.html"):
                return self.send_bytes((STATIC / "index.html").read_bytes(), MIME[".html"])
            if u.path == "/tree":
                return self.send_bytes(site.build().read_bytes(), MIME[".html"])
            if u.path.startswith("/static/"):
                p = (STATIC / u.path[len("/static/"):]).resolve()
                if STATIC.resolve() not in p.parents or not p.is_file():
                    return self.send_json({"error": "not_found"}, 404)
                return self.send_bytes(p.read_bytes(), MIME.get(p.suffix, "application/octet-stream"))
            if u.path == "/api/health":  # code_version để launcher biết server đang chạy bản cũ
                return self.send_json({"ok": True, "code_version": int(CODE_MTIME), "features": ["modules", "cycle", "news"]})
            if u.path == "/api/status":
                return self.send_json(self.status())
            if u.path == "/api/team":
                return self.send_json(team_list())
            if u.path == "/api/modules":
                return self.send_json(modules_list())
            if u.path == "/api/reports":
                return self.send_json(list_reports())
            if u.path == "/api/report":
                p = safe_path(q.get("path", ""), REPORTS)
                text = p.read_text(encoding="utf-8")
                title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), p.stem)
                body = re.sub(r"^# .*\n?", "", text, count=1, flags=re.M).replace("\n## ", "\n### ")
                return self.send_json({"title": title, "html": site.md_to_html(body), "path": q.get("path")})
            if u.path == "/api/report.docx":
                p = safe_path(q.get("path", ""), REPORTS)
                md = p.read_text(encoding="utf-8")
                sub = f"{p.parent.name} · Xuất ngày {dt.date.today().strftime('%d/%m/%Y')} · Phòng R&D Năng lượng & Công nghệ – VTICorp"
                return self.send_docx(docx_export.markdown_to_docx(md, subtitle=sub), docx_name(p.parent.name, p.stem))
            if u.path == "/api/chat.docx":
                h = chat_history()
                items = h if q.get("i") in (None, "", "all") else [h[int(q["i"])]]
                md = "\n\n".join(chat_md(it) for it in items)
                title = "Hỏi đáp Phòng R&D VTI" if len(items) > 1 else f"Hỏi đáp: {items[0]['q'][:80]}"
                return self.send_docx(docx_export.markdown_to_docx(md, title=title), docx_name("HoiDap", dt.datetime.now().strftime("%Y%m%d_%H%M")))
            if u.path == "/api/news":
                d = news_load(q.get("date"))
                return self.send_json({"days": news_days(), "digest": d,
                                       "running": any(j["kind"] == "news" and j["state"] == "running" for j in JOBS.values())})
            if u.path == "/api/news.docx":
                d = news_load(q.get("date"))
                if not d:
                    return self.send_json({"error": "Chưa có bản tin"}, 404)
                return self.send_docx(docx_export.markdown_to_docx(news.to_markdown(d)), docx_name("BanTin", d["date"]))
            if u.path == "/api/library":
                return self.send_json(self.library())
            if u.path == "/api/chat":
                return self.send_json(chat_history())
            if u.path == "/api/job":
                j = JOBS.get(q.get("id", ""))
                return self.send_json(j or {"state": "missing"}, 200 if j else 404)
            if u.path == "/api/jobs":
                return self.send_json(sorted(JOBS.values(), key=lambda j: j["started"], reverse=True)[:20])
            return self.send_json({"error": "not_found"}, 404)
        except Exception as e:
            return self.send_json({"error": f"{type(e).__name__}: {e}"}, 400)

    # ---------------- POST
    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if not self.authorized(u):
            return self.deny()
        q = dict(urllib.parse.parse_qsl(u.query))
        try:
            if u.path == "/api/ask":
                b = self.jbody()
                question = (b.get("question") or "").strip()
                if not question:
                    return self.send_json({"error": "Câu hỏi trống"}, 400)
                return self.send_json({"job": start_job("ask", job_ask, question, b.get("agent") or None, b.get("module") or None)})
            if u.path in ("/api/week", "/api/cycle"):
                b = self.jbody()
                mods = [m for m in (b.get("modules") or []) if m in M.load()]
                return self.send_json({"job": start_job("cycle", job_cycle, b.get("focus", ""), mods)})
            if u.path == "/api/modules":
                b = self.jbody()
                if not (b.get("name") or "").strip() or not (b.get("goal") or "").strip():
                    return self.send_json({"error": "Cần nhập tên và mục tiêu module"}, 400)
                for k in ("start", "deadline"):
                    if b.get(k):
                        dt.date.fromisoformat(b[k])
                form = {k: str(b.get(k) or "").strip() for k in ("name", "icon", "goal", "scope", "questions", "references", "start", "deadline", "status")}
                if form["status"] not in M.STATUSES:
                    form["status"] = "active"
                return self.send_json({"job": start_job("module", job_new_module, form)})
            if u.path == "/api/modules/status":
                b = self.jbody()
                return self.send_json(M.set_status(str(b.get("id")), str(b.get("status"))))
            if u.path == "/api/news/refresh":
                b = self.jbody()
                return self.send_json({"job": start_job("news", job_news, bool(b.get("ai", True)))})
            if u.path == "/api/ingest":
                return self.send_json({"job": start_job("ingest", job_ingest)})
            if u.path == "/api/upload":
                folder = q.get("folder", "01_standards")
                name = os.path.basename(q.get("name", ""))
                if not re.match(r"^(\d\d_[a-z_]+|m_[a-z0-9_]+)$", folder) or not name or Path(name).suffix.lower() not in {".pdf", ".md", ".txt"}:
                    return self.send_json({"error": "Chỉ nhận PDF/MD/TXT vào thư mục library/NN_xxx hoặc library/m_<module>"}, 400)
                dest = LIB / folder
                dest.mkdir(parents=True, exist_ok=True)
                (dest / name).write_bytes(self.body())
                return self.send_json({"ok": True, "saved": f"library/{folder}/{name}"})
            if u.path == "/api/thermal":
                b = self.jbody()
                p = th.ThermalParams(cooling=b.get("cooling", "ONAF"), R=float(b.get("R", 6)),
                                     d_theta_or=float(b.get("dtor", 45)), d_theta_hr=float(b.get("dthr", 35)))
                hours = max(1.0, min(72.0, float(b.get("hours", 24))))
                n = int(hours * 60 / 3)
                prof = b.get("profile") or [float(b.get("load", 1.0))] * 24
                load = [float(prof[int(i * 3 / 60) % len(prof)]) for i in range(n)]
                amb = [float(b.get("ambient", 30))] * n
                res = th.simulate(load, amb, 3.0, p)
                step = max(1, len(res) // 240)
                return self.send_json({
                    "series": [{k: round(r[k], 2) for k in ("t_min", "K", "theta_o", "theta_h", "V")} for r in res[::step]],
                    "max_theta_h": round(max(r["theta_h"] for r in res), 1),
                    "loss_of_life_h": round(res[-1]["loss_of_life_h"], 1),
                    "max_load_120": round(th.max_load_for_hotspot(120, float(b.get("ambient", 30)), p), 2),
                    "max_load_140": round(th.max_load_for_hotspot(140, float(b.get("ambient", 30)), p), 2)})
            if u.path == "/api/dga":
                b = self.jbody()
                vals = [float(b.get(k, 0)) for k in ("h2", "ch4", "c2h2", "c2h4", "c2h6")]
                opt = lambda k: float(b[k]) if b.get(k) not in (None, "") else None
                return self.send_json(dga.diagnose(*vals, co=opt("co"), co2=opt("co2"),
                                                   oltc_communicating=bool(b.get("oltc"))))
            if u.path == "/api/scl":
                tmp = DATA / "upload.scd"
                DATA.mkdir(exist_ok=True)
                tmp.write_bytes(self.body())
                m = scl.parse_scl(str(tmp))
                return self.send_json({"model": m, "signals": scl.condition_signals(m)})
            if u.path == "/api/chat/clear":
                CHAT.unlink(missing_ok=True)
                return self.send_json({"ok": True})
            return self.send_json({"error": "not_found"}, 404)
        except Exception as e:
            return self.send_json({"error": f"{type(e).__name__}: {e}"}, 400)

    # ---------------- data
    def status(self):
        s, _ = load_cfg()
        from lab.hardware import total_ram_gb
        from lab.knowledge import KnowledgeBase
        try:
            llm = get_llm(s)
            models = llm.list_models()
            cloud = {"enabled": bool(llm.cloud), "lines": llm.status(), "next": llm.route("director", False)}
            chat_model = llm.chat_model
        except Exception as e:
            models, cloud, chat_model = [], {"enabled": False, "lines": [str(e)], "next": "local"}, "?"
        mods = M.load()
        return {"phase": phase_now(), "project": s.get("project", {}),
                "modules": {"total": len(mods), "active": sum(1 for m in mods.values() if m.get("status") == "active")}, "ram_gb": round(total_ram_gb()),
                "ollama_ok": bool(models), "models": models, "chat_model": chat_model,
                "embed_model": s["ollama"]["embed_model"], "cloud": cloud,
                "kb": KnowledgeBase(s["paths"]["index_db"]).stats(), "reports": len(list_reports()),
                "jobs_running": sum(1 for j in JOBS.values() if j["state"] == "running")}

    def library(self):
        out = []
        mods = M.load()
        owner = {d: mid for mid, m in mods.items() for d in (m.get("library") or [])}
        for mid, m in mods.items():
            for d in (m.get("library") or []):
                if d.startswith("m_"):
                    (LIB / d).mkdir(parents=True, exist_ok=True)
        for d in sorted(p for p in LIB.iterdir() if p.is_dir()):
            files = [{"name": f.name, "kb": round(f.stat().st_size / 1024)} for f in sorted(d.iterdir())
                     if f.is_file() and not f.name.startswith(".")]
            mid = owner.get(d.name)
            out.append({"folder": d.name, "files": files, "module": mid or "",
                        "module_name": (mods.get(mid) or {}).get("name", "") if mid else "",
                        "module_icon": (mods.get(mid) or {}).get("icon", "") if mid else ""})
        return out


def main():
    DATA.mkdir(exist_ok=True)
    start_job("ingest", job_ingest)  # tự nạp tài liệu mới trong library/ mỗi lần server khởi động
    threading.Thread(target=news_scheduler, daemon=True).start()  # bản tin năng lượng hằng ngày
    threading.Thread(target=cycle_scheduler, daemon=True).start()  # báo cáo nghiên cứu mỗi 3 ngày
    threading.Thread(target=code_watcher, daemon=True).start()  # tự nạp bản code mới
    host = "0.0.0.0" if remote_cfg().get("token") else "127.0.0.1"
    srv = ThreadingHTTPServer((host, PORT), Handler)
    print(f"VTI R&D Lab đang chạy: http://localhost:{PORT}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
