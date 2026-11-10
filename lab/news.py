"""Tổng hợp tin tức ngành năng lượng hằng ngày + phát hiện cơ hội hợp tác cho VTI.

Nguồn: Google News RSS (truy vấn tiếng Việt/tiếng Anh), RSS các trang ngành, arXiv API (bài nghiên cứu).
Chỉ dùng thư viện chuẩn (urllib + xml.etree). Chạy trên máy anh Khương nên truy cập Internet trực tiếp.
Kết quả lưu data/news/YYYY-MM-DD.json; Qwen (tùy chọn) viết tóm tắt + gợi ý hành động cho các tin điểm cao.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DT-RnD-Lab/1.0 news-digest"
TZ = dt.timezone(dt.timedelta(hours=7))

CATEGORIES = {
    "tender": "Đấu thầu",
    "project": "Dự án & kế hoạch",
    "research": "Nghiên cứu & bài báo",
    "news": "Tin tức",
}
PROJECT_WORDS = ["dự án", "khởi công", "đóng điện", "phê duyệt", "quy hoạch", "kế hoạch", "đầu tư", "nâng cấp",
                 "cải tạo", "xây dựng", "vận hành thương mại", "project", "plan", "approve", "construction",
                 "commission", "investment", "build", "expansion"]
TENDER_WORDS = ["đấu thầu", "mời thầu", "gói thầu", "trúng thầu", "tender", "rfp", "bid", "procurement", "awarded"]
RESEARCH_WORDS = ["nghiên cứu", "báo cáo", "study", "paper", "research", "report", "analysis"]


# ------------------------------------------------------------------ fetch & parse
def google_news_url(q: str, lang: str) -> str:
    if lang == "vi":
        return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": q + " when:3d", "hl": "vi", "gl": "VN", "ceid": "VN:vi"})
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q + " when:3d", "hl": "en-US", "gl": "US", "ceid": "US:en"})


def arxiv_url(q: str) -> str:
    return "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": 15})


def fetch(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _text(el, *names) -> str:
    for n in names:
        x = el.find(n)
        if x is not None and (x.text or "").strip():
            return x.text.strip()
    return ""


def _clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def _date(s: str) -> str:
    if not s:
        return ""
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return ""
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(TZ).isoformat(timespec="minutes")


def parse_feed(data: bytes, source: dict) -> list[dict]:
    """Đọc RSS 2.0 hoặc Atom (arXiv)."""
    root = ET.fromstring(data)
    out = []
    atom = "{http://www.w3.org/2005/Atom}"
    if root.tag.endswith("feed"):  # Atom
        for e in root.findall(f"{atom}entry"):
            link = ""
            for l in e.findall(f"{atom}link"):
                if l.get("rel") in (None, "alternate"):
                    link = l.get("href", "")
                    break
            authors = ", ".join(_text(a, f"{atom}name") for a in e.findall(f"{atom}author")[:3])
            out.append({"title": _clean(_text(e, f"{atom}title")), "link": link,
                        "summary": _clean(_text(e, f"{atom}summary", f"{atom}content"))[:600],
                        "published": _date(_text(e, f"{atom}published", f"{atom}updated")),
                        "publisher": ("arXiv · " + authors) if "arxiv" in source.get("url", "") else source["name"]})
        return out
    for it in root.iter("item"):
        title = _clean(_text(it, "title"))
        publisher = _text(it, "source") or source["name"]
        if source.get("google") and " - " in title:  # Google News: "Tiêu đề - Tên báo"
            title, publisher = title.rsplit(" - ", 1)[0], title.rsplit(" - ", 1)[1]
        out.append({"title": title, "link": _text(it, "link"),
                    "summary": _clean(_text(it, "description"))[:600],
                    "published": _date(_text(it, "pubDate", "{http://purl.org/dc/elements/1.1/}date")),
                    "publisher": publisher})
    return out


def build_sources(cfg: dict) -> list[dict]:
    src = []
    for q in cfg.get("google_news_vn", []):
        src.append({"name": f"Google News VN · {q}", "url": google_news_url(q, "vi"), "region": "vn", "kind": "news",
                    "google": True, "query": q})
    for q in cfg.get("google_news_intl", []):
        src.append({"name": f"Google News · {q}", "url": google_news_url(q, "en"), "region": "intl", "kind": "news",
                    "google": True, "query": q})
    for r in cfg.get("rss", []):
        src.append({**r})
    for q in cfg.get("arxiv", []):
        src.append({"name": "arXiv", "url": arxiv_url(q), "region": "intl", "kind": "research", "query": q})
    return src


# ------------------------------------------------------------------ chấm điểm
def _score(text: str, table: dict) -> tuple[int, list[str]]:
    t = text.lower()
    hit = [k for k in table if k in t]
    return sum(table[k] for k in hit), hit


def classify(item: dict, source: dict, cfg: dict) -> dict:
    text = f"{item['title']} {item['summary']}"
    low = text.lower()
    rel, rel_hit = _score(text, cfg.get("vti_keywords", {}))
    opp, opp_hit = _score(text, cfg.get("opportunity_keywords", {}))
    if source.get("kind") == "research":
        cat = "research"
    elif any(w in low for w in TENDER_WORDS):
        cat = "tender"
    elif any(w in low for w in PROJECT_WORDS):
        cat = "project"
    elif any(w in low for w in RESEARCH_WORDS):
        cat = "research"
    else:
        cat = "news"
    score = rel + opp
    is_opp = rel >= 5 and (opp >= 4 or cat in ("tender", "project"))
    reasons = []
    if rel_hit:
        reasons.append("liên quan năng lực VTI: " + ", ".join(rel_hit[:6]))
    if opp_hit:
        reasons.append("tín hiệu cơ hội: " + ", ".join(opp_hit[:5]))
    return {**item, "region": source.get("region", "intl"), "kind": source.get("kind", "news"),
            "category": cat, "category_vi": CATEGORIES[cat], "relevance": rel, "opportunity": opp,
            "score": score, "is_opportunity": is_opp, "reasons": reasons, "query": source.get("query", "")}


def _norm(t: str) -> str:
    t = re.sub(r"\s+[-–|]\s+[^-–|]{2,40}$", "", t)  # bỏ hậu tố " - Tên báo"
    return re.sub(r"[^\w]+", " ", t.lower()).strip()[:90]


# ------------------------------------------------------------------ chạy
def collect(cfg: dict, log=print, fetcher=fetch) -> dict:
    sources = build_sources(cfg)
    status, items = [], []
    max_age = dt.timedelta(hours=int(cfg.get("max_age_hours", 72)))
    now = dt.datetime.now(TZ)

    def one(s):
        try:
            return s, parse_feed(fetcher(s["url"]), s), None
        except Exception as e:  # nguồn lỗi không làm hỏng cả bản tin
            return s, [], f"{type(e).__name__}: {e}"[:160]

    with ThreadPoolExecutor(max_workers=8) as ex:
        for s, got, err in ex.map(one, sources):
            status.append({"name": s["name"], "ok": err is None, "count": len(got), "error": err})
            log(f"{'✓' if err is None else '✗'} {s['name']} ({len(got)})" + (f" – {err}" if err else ""))
            for it in got:
                if not it["title"] or not it["link"]:
                    continue
                if it["published"]:
                    try:
                        if now - dt.datetime.fromisoformat(it["published"]) > max_age and s.get("kind") != "research":
                            continue
                    except Exception:
                        pass
                c = classify(it, s, cfg)
                # nguồn RSS tổng hợp (không phải truy vấn chuyên đề) → chỉ giữ tin liên quan ngành
                if not s.get("google") and s.get("kind") != "research" and c["relevance"] < 3:
                    continue
                items.append(c)
    key = lambda x: (x["score"], x["published"] or "")
    seen, uniq = set(), []
    for it in sorted(items, key=key, reverse=True):  # giữ bản điểm cao nhất của tin trùng
        k = _norm(it["title"])
        if k not in seen and it["link"] not in seen:
            seen.update((k, it["link"]))
            uniq.append(it)
    return {"date": now.date().isoformat(), "fetched_at": now.isoformat(timespec="minutes"),
            "sources": status, "items": uniq}


def ai_enrich(digest: dict, llm, top: int = 8, log=print) -> dict:
    """Qwen viết tóm tắt 1–2 câu + gợi ý hành động cho VTI cho các tin điểm cao nhất (ưu tiên cơ hội)."""
    pool = sorted(digest["items"], key=lambda x: (not x["is_opportunity"], -x["score"]))[:top]
    system = ("Bạn là chuyên viên phát triển kinh doanh của VTICorp – công ty Việt Nam cung cấp giải pháp giám sát online "
              "thiết bị cao áp (nhiệt độ không dây, DGA, phóng điện cục bộ, sợi quang DTS), thí nghiệm–hiệu chỉnh trạm "
              "đến 500 kV, và đang nghiên cứu Digital Twin máy biến áp/trạm. Viết tiếng Việt, ngắn gọn, thực tế; "
              "không bịa thông tin ngoài tiêu đề và đoạn trích.")
    for it in pool:
        prompt = (f"Tin: {it['title']}\nNguồn: {it['publisher']} ({it['published']})\nTrích: {it['summary'][:500]}\n\n"
                  'Trả JSON {"tom_tat":"1–2 câu","co_hoi":"cơ hội/hợp tác cụ thể cho VTI hoặc \'không rõ\'",'
                  '"hanh_dong":"1 việc nên làm tiếp (liên hệ ai, theo dõi gì)"}')
        try:
            r = llm.chat_json(system, prompt, role="vn_market")
            it["ai"] = {k: str(r.get(k, ""))[:400] for k in ("tom_tat", "co_hoi", "hanh_dong")}
            log(f"AI ✓ {it['title'][:60]}")
        except Exception as e:
            log(f"AI ✗ {it['title'][:60]}: {e}")
    digest["ai_at"] = dt.datetime.now(TZ).isoformat(timespec="minutes")
    return digest


def save(digest: dict, folder: Path, keep_days: int = 60) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{digest['date']}.json"
    p.write_text(json.dumps(digest, ensure_ascii=False, indent=1), encoding="utf-8")
    cutoff = (dt.date.today() - dt.timedelta(days=keep_days)).isoformat()
    for f in folder.glob("*.json"):
        if f.stem < cutoff:
            f.unlink(missing_ok=True)
    return p


def to_markdown(d: dict) -> str:
    def block(title, items):
        if not items:
            return ""
        lines = [f"## {title}"]
        for it in items:
            lines.append(f"- **{it['title']}** – {it['publisher']} ({(it['published'] or '')[:16].replace('T', ' ')}) "
                         f"[link]({it['link']})")
            if it.get("ai"):
                lines.append(f"   Tóm tắt: {it['ai'].get('tom_tat', '')} Cơ hội VTI: {it['ai'].get('co_hoi', '')} "
                             f"Việc nên làm: {it['ai'].get('hanh_dong', '')}")
            elif it["reasons"]:
                lines.append(f"   ({'; '.join(it['reasons'])})")
        return "\n".join(lines) + "\n"
    items = d["items"]
    opp = [x for x in items if x["is_opportunity"]][:15]
    md = [f"# Bản tin năng lượng & cơ hội VTI – {d['date']}",
          f"Cập nhật {d['fetched_at'].replace('T', ' ')} · {len(items)} tin từ "
          f"{sum(1 for s in d['sources'] if s['ok'])}/{len(d['sources'])} nguồn.\n",
          block("🎯 Cơ hội hợp tác cho VTI", opp),
          block("📝 Đấu thầu", [x for x in items if x["category"] == "tender"][:15]),
          block("🏗 Dự án & kế hoạch – trong nước", [x for x in items if x["category"] == "project" and x["region"] == "vn"][:15]),
          block("🏗 Dự án & kế hoạch – quốc tế", [x for x in items if x["category"] == "project" and x["region"] == "intl"][:10]),
          block("📰 Tin tức trong nước", [x for x in items if x["category"] == "news" and x["region"] == "vn"][:15]),
          block("🌏 Tin tức quốc tế", [x for x in items if x["category"] == "news" and x["region"] == "intl"][:12]),
          block("🔬 Nghiên cứu & bài báo", [x for x in items if x["category"] == "research"][:12])]
    return "\n".join(m for m in md if m)
