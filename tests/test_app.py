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
    assert team[0]["key"] == "director" and len({p["key"] for p in team}) == len(team) >= 15
    assert all("look" in p and p.get("module") for p in team)
    mods = json.loads(call("/api/modules")[1])
    assert {m["id"] for m in mods} >= {"dt", "monitoring", "asset_health", "bess", "market"}
    assert call("/api/modules", {"name": ""})[0] == 400
    assert call("/api/modules/status", {"id": "dt", "status": "xx"})[0] == 400
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
    assert "VTICorp" in z.read("word/document.xml").decode()


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
        def chat_json(self, *a, **k): return {"members": ["benchmark"], "keywords_en": "monitoring guide"}
        def chat(self, system, user, **k):
            self.prompt = user
            return "## Trả lời ngắn\nok [S1]"
    s = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    t = yaml.safe_load((ROOT / "config/team.yaml").read_text(encoding="utf-8"))
    f = Fake()
    boss = Director(t, s, f, kb)
    boss.web_get = fake_web
    out = boss.ask("IEEE C57.143 bản mới nhất?")
    assert "báo cáo tuần" in f.prompt and "## Nguồn trong kho" in out and "FS02" in out
    assert "NGUỒN INTERNET" in f.prompt and "[W1]" in f.prompt and "## Nguồn Internet" in out


BING = b"""<?xml version="1.0"?><rss><channel>
<item><title>IEEE C57.143-2024 Guide for Application of Monitoring Equipment</title><link>https://standards.ieee.org/ieee/C57.143/x</link><description>monitoring guide</description></item>
<item><title>Blog random</title><link>https://random-blog.example/post</link><description>monitoring guide blog</description></item>
</channel></rss>"""
PAGE = (b"<html><head><title>IEEE C57.143-2024</title><script>var x=1</script></head><body><nav>menu</nav>"
        b"<p>IEEE C57.143-2024 is the guide for application of monitoring equipment to liquid-immersed transformers.</p>"
        b"<p>Unrelated cookie text that is long enough to be a paragraph but has nothing to do with it.</p></body></html>")


def fake_web(url, timeout=20, data=None, accept="*/*"):
    if "bing.com" in url:
        return BING, "application/rss+xml"
    if "duckduckgo" in url or "openalex" in url:
        raise OSError("blocked")
    return PAGE, "text/html"


def test_web_research_ranking_and_verify(tmp_path):
    from lab import web as W
    cfg = W.load_cfg()
    assert W.tier("https://standards.ieee.org/x", cfg) == "official" and W.tier("https://www.hitachienergy.com/a", cfg) == "official"
    assert W.tier("https://baodauthau.vn/a", cfg) == "trusted" and W.tier("https://abc.xyz", cfg) == "other"
    assert W.vendor_domains("so sánh Hitachi Energy và Siemens Energy", cfg)[:2] == ["hitachienergy.com", "siemens-energy.com"]
    assert W.vendor_domains("change management", cfg) == []  # 'GE' không khớp giữa từ
    qs = W.build_queries("Hitachi TXpert có những tính năng gì?", "TXpert digital transformer", cfg)
    assert any(q.startswith("site:hitachienergy.com") for q in qs)
    assert W.build_queries("Khách hàng ABC trạm X", "transformer DGA", cfg, safe_only_keywords=True)[0] == "transformer DGA"
    r = W.research("IEEE C57.143 monitoring guide", "monitoring guide", cfg, get=fake_web, cache_dir=tmp_path)
    assert r.sources[0].tier == "official" and "liquid-immersed" in r.sources[0].excerpt and "var x" not in r.sources[0].excerpt
    assert any("duckduckgo" in e for e in r.errors)
    assert "[W1]" in r.context() and "standards.ieee.org" in r.markdown()
    miss = W.verify_claims("Theo IEEE C57.143-2024 [W1] và IEC 60599, ngưỡng là 150 ppm, hiệu suất 99,5 %.", r.all_text())
    assert "IEC 60599" in miss and "150 ppm" in miss and not any("C57.143" in m for m in miss)


def test_news_collect_classify_and_api():
    import datetime as dt
    import yaml
    from lab import news
    cfg = yaml.safe_load((ROOT / "config/news.yaml").read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    rss = f"""<?xml version="1.0"?><rss><channel>
<item><title>EVNNPT mời thầu gói giám sát trực tuyến máy biến áp 220kV - Báo Công Thương</title><link>https://x/1</link><pubDate>{now}</pubDate></item>
<item><title>Giá vàng hôm nay - VnExpress</title><link>https://x/2</link><pubDate>{now}</pubDate></item></channel></rss>""".encode()
    d = news.collect(cfg, log=lambda *a: None, fetcher=lambda u: rss)
    top = d["items"][0]
    assert top["is_opportunity"] and top["category"] == "tender" and top["publisher"] == "Báo Công Thương"
    assert len([x for x in d["items"] if x["link"] == "https://x/1"]) == 1
    assert "Cơ hội hợp tác" in news.to_markdown(d)
    import tempfile
    server.NEWS_DIR = Path(tempfile.mkdtemp())
    news.save(d, server.NEWS_DIR)
    r = json.loads(call("/api/news")[1])
    assert r["digest"]["date"] == d["date"] and d["date"] in r["days"]
    assert call(f"/api/news.docx?date={d['date']}")[1][:2] == b"PK"
