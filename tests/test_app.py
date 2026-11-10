"""Kiểm tra nhanh API của ứng dụng web (không cần Ollama)."""
import json
import urllib.parse
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))
import server  # noqa: E402

srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"


def call(path, body=None, raw=False):
    data = None if body is None else (body if raw else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, data=data)) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_pages_and_static():
    assert call("/")[0] == 200 and b"DT-RnD" in call("/")[1]
    assert call("/static/js/main.js")[0] == 200
    assert call("/static/../config/settings.yaml")[0] == 404


def test_team_reports_phase():
    team = json.loads(call("/api/team")[1])
    assert len(team) == 8 and team[0]["key"] == "director"
    assert isinstance(json.loads(call("/api/reports")[1]), list)
    p = server.phase_now("2027-02-01")
    assert p["code"] == "GĐ3" and 0 < p["pct"] < 1


def test_report_path_traversal_blocked():
    assert call("/api/report?path=../config/settings.yaml")[0] == 400


def test_tools():
    r = json.loads(call("/api/thermal", {"load": 1.0, "ambient": 20, "hours": 6})[1])
    assert 90 < r["max_theta_h"] < 115
    d = json.loads(call("/api/dga", {"h2": 100, "ch4": 120, "c2h2": 1, "c2h4": 50, "c2h6": 65})[1])
    assert d["duval"] == "T2"
    s = json.loads(call("/api/scl", (ROOT / "tests/data/sample.scd").read_bytes(), raw=True)[1])
    assert any(x["class"] == "SIML" for x in s["signals"])


def test_upload_rejects_bad_folder():
    assert call("/api/upload?folder=../x&name=a.pdf", b"x", raw=True)[0] == 400


def test_report_docx_export():
    import io
    import zipfile
    rep = json.loads(call("/api/reports")[1])[0]["path"]
    code, data = call("/api/report.docx?path=" + urllib.parse.quote(rep))
    assert code == 200 and data[:2] == b"PK"
    z = zipfile.ZipFile(io.BytesIO(data))
    assert "word/document.xml" in z.namelist()
    assert "Digital Twin" in z.read("word/document.xml").decode()


def test_docx_markdown_features():
    from lab.docx_export import markdown_to_docx
    import io
    import zipfile
    d = markdown_to_docx("# T\n## H\n1. a\n2. b\n- x\n| a | b |\n|---|---|\n| 1 | 2 |\n[l](https://x.y)")
    z = zipfile.ZipFile(io.BytesIO(d))
    doc = z.read("word/document.xml").decode()
    assert "<w:tbl>" in doc and "w:numId" in doc and "w:hyperlink" in doc


def test_kb_entity_coverage_and_direct_answer():
    import tempfile
    import yaml
    from lab.knowledge import KnowledgeBase
    from lab.team import Director
    kb = KnowledgeBase(tempfile.mktemp(suffix=".sqlite"))
    kb.ingest(str(ROOT / "library"), log=lambda *a: None)
    files = [h.source for h in kb.search("so sánh kiến trúc DT của Siemens và Hitachi", 10)]
    assert any("Siemens" in f for f in files) and any("Hitachi" in f for f in files)

    class Fake:
        last_engine = "fake"
        def chat_json(self, *a, **k): return {"members": ["benchmark"]}
        def chat(self, system, user, **k):
            self.prompt = user
            return "## Trả lời ngắn\nok [S1]"
    s = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    t = yaml.safe_load((ROOT / "config/team.yaml").read_text(encoding="utf-8"))
    f = Fake()
    out = Director(t, s, f, kb).ask("IEEE C57.143 bản mới nhất?")
    assert "báo cáo tuần" in f.prompt and "## Nguồn trong kho" in out and "FS02" in out
