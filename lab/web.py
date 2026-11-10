"""Nghiên cứu trên Internet cho các chuyên viên AI – chỉ lấy thông tin có nguồn, ưu tiên website chính thức.

Luồng: tạo truy vấn (kể cả truy vấn site:<hãng> khi câu hỏi nhắc tới hãng) → tìm qua nhiều công cụ
(Bing RSS, DuckDuckGo HTML, Google News RSS, OpenAlex cho bài báo khoa học) → xếp hạng theo độ tin cậy tên miền
(config/web_sources.yaml) → tải trang, bóc chữ, chọn các đoạn liên quan nhất → đưa vào prompt dưới dạng [W#] kèm URL.
Sau khi Qwen trả lời, verify_claims() dò các số liệu/số hiệu tiêu chuẩn KHÔNG xuất hiện trong nguồn nào và cảnh báo.

Không gửi dữ liệu khách hàng ra Internet: khi tài liệu nhạy cảm tham gia câu trả lời, chỉ dùng từ khóa kỹ thuật chung.
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "web_sources.yaml"
CACHE_DIR = ROOT / "data" / "web_cache"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
TIER_VI = {"official": "Chính thức", "trusted": "Uy tín", "other": "Chưa xác minh"}
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


# ------------------------------------------------------------------ cấu hình
def load_cfg(path: Path | str | None = None) -> dict:
    p = Path(path or CFG_PATH)
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    cfg = cfg or {}
    cfg.setdefault("enabled", True)
    cfg.setdefault("max_pages", 5)
    cfg.setdefault("excerpt_chars", 1400)
    cfg.setdefault("engines", ["bing", "duckduckgo", "openalex"])
    cfg.setdefault("allow_other_domains", True)
    cfg.setdefault("official", [])
    cfg.setdefault("trusted", [])
    cfg.setdefault("vendors", {})
    return cfg


def domain_of(url: str) -> str:
    d = urllib.parse.urlparse(url).netloc.lower()
    return d[4:] if d.startswith("www.") else d


def tier(url: str, cfg: dict) -> str:
    d = domain_of(url)
    match = lambda lst: any(d == x or d.endswith("." + x) for x in lst)  # noqa: E731
    if match(cfg["official"]) or match([dom for v in cfg["vendors"].values() for dom in v]):
        return "official"
    if match(cfg["trusted"]):
        return "trusted"
    return "other"


# ------------------------------------------------------------------ mạng
def http_get(url: str, timeout: int = 20, data: bytes | None = None, accept: str = "*/*") -> tuple[bytes, str]:
    """GET/POST có thử lại không qua proxy khi proxy hệ thống chặn (403 Tunnel / ProxyError)."""
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": accept,
                                                         "Accept-Language": "vi,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(3_000_000), r.headers.get("Content-Type", "")
    except (urllib.error.URLError, OSError) as e:
        if isinstance(e, urllib.error.HTTPError) and e.code not in (403, 407):
            raise
        with _DIRECT.open(req, timeout=timeout) as r:
            return r.read(3_000_000), r.headers.get("Content-Type", "")


@dataclass
class Result:
    title: str
    url: str
    snippet: str = ""
    engine: str = ""
    date: str = ""


def _strip(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(s or ""))).strip()


def search_bing(q: str, n: int, get=http_get) -> list[Result]:
    raw, _ = get("https://www.bing.com/search?" + urllib.parse.urlencode({"format": "rss", "q": q, "count": n}),
                 accept="application/rss+xml, */*")
    root = ET.fromstring(raw)
    out = []
    for it in root.iter("item"):
        link = (it.findtext("link") or "").strip()
        if link.startswith("http"):
            out.append(Result(_strip(it.findtext("title") or ""), link, _strip(it.findtext("description") or ""),
                              "bing", (it.findtext("pubDate") or "")[:16]))
    return out[:n]


def search_ddg(q: str, n: int, get=http_get) -> list[Result]:
    raw, _ = get("https://html.duckduckgo.com/html/", data=urllib.parse.urlencode({"q": q}).encode(), accept="text/html")
    page = raw.decode("utf-8", "ignore")
    out = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<a[^>]+class="result__a"|$)',
                         page, flags=re.S):
        href, title, rest = m.group(1), m.group(2), m.group(3)
        if "uddg=" in href:
            href = urllib.parse.unquote(urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("uddg", [href])[0])
        sn = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', rest, flags=re.S)
        if href.startswith("http"):
            out.append(Result(_strip(title), href, _strip(sn.group(1)) if sn else "", "duckduckgo"))
        if len(out) >= n:
            break
    return out


def search_openalex(q: str, n: int, get=http_get) -> list[Result]:
    """Bài báo khoa học (OpenAlex – miễn phí, không cần khóa). Trả về DOI/landing page + tóm tắt."""
    raw, _ = get("https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": q, "per-page": n, "sort": "relevance_score:desc"}), accept="application/json")
    out = []
    for w in json.loads(raw).get("results", [])[:n]:
        inv = w.get("abstract_inverted_index") or {}
        words = sorted(((p, t) for t, ps in inv.items() for p in ps))
        abstract = " ".join(t for _, t in words)[:1500]
        url = (w.get("primary_location") or {}).get("landing_page_url") or w.get("doi") or w.get("id")
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        out.append(Result(w.get("display_name") or "", url, f"{venue} ({w.get('publication_year', '')}). {abstract}",
                          "openalex", str(w.get("publication_year") or "")))
    return out


ENGINES = {"bing": search_bing, "duckduckgo": search_ddg, "openalex": search_openalex}


# ------------------------------------------------------------------ bóc chữ trang
class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "aside"}

    def __init__(self):
        super().__init__()
        self.parts, self.skip, self.title = [], 0, ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag == "title":
            self._in_title = True
        if tag in ("p", "li", "tr", "h1", "h2", "h3", "h4", "br", "div", "td", "th"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self.skip:
            self.parts.append(data)


def html_to_text(raw: bytes) -> tuple[str, str]:
    p = _Text()
    try:
        p.feed(raw.decode("utf-8", "ignore"))
    except Exception:
        pass
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(p.parts))
    text = "\n".join(l.strip() for l in text.splitlines() if len(l.strip()) > 2)
    return p.title.strip(), text


def pdf_to_text(raw: bytes, max_pages: int = 25) -> str:
    try:
        from pypdf import PdfReader
        r = PdfReader(io.BytesIO(raw))
        return "\n".join((pg.extract_text() or "") for pg in r.pages[:max_pages])
    except Exception:
        return ""


def fetch_page(url: str, get=http_get, ttl_days: int = 7, cache_dir: Path | None = CACHE_DIR) -> tuple[str, str]:
    """(title, text) có cache trên đĩa để không tải lại."""
    key = hashlib.sha1(url.encode()).hexdigest()
    cf = cache_dir / f"{key}.json" if cache_dir else None
    if cf and cf.exists() and time.time() - cf.stat().st_mtime < ttl_days * 86400:
        d = json.loads(cf.read_text(encoding="utf-8"))
        return d["title"], d["text"]
    raw, ctype = get(url, accept="text/html,application/pdf,*/*")
    if "pdf" in ctype.lower() or url.lower().endswith(".pdf") or raw[:4] == b"%PDF":
        title, text = Path(urllib.parse.urlparse(url).path).name, pdf_to_text(raw)
    else:
        title, text = html_to_text(raw)
    text = text[:60000]
    if cf:
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps({"url": url, "title": title, "text": text}, ensure_ascii=False), encoding="utf-8")
    return title, text


_TOK = re.compile(r"[\wÀ-ỹ]+", re.U)
_STOP = {"the", "and", "for", "with", "of", "in", "to", "a", "an", "is", "are", "on", "by", "or", "và", "của", "cho", "là",
         "các", "những", "có", "không", "với", "trong", "được", "một", "này", "như", "nào", "gì", "thế", "để"}


def _terms(s: str) -> set[str]:
    return {t for t in (x.lower() for x in _TOK.findall(s)) if len(t) > 1 and t not in _STOP}


def best_passages(text: str, query: str, limit: int = 1400) -> str:
    """Chọn các đoạn có nhiều từ khóa nhất (giữ thứ tự gốc)."""
    q = _terms(query)
    paras = [p for p in re.split(r"\n+", text) if len(p) > 40]
    if not paras:
        return text[:limit]
    scored = sorted(range(len(paras)), key=lambda i: -len(q & _terms(paras[i])))
    keep, size = [], 0
    for i in scored:
        if size > limit:
            break
        if not q & _terms(paras[i]) and keep:
            break
        keep.append(i)
        size += len(paras[i])
    return "\n".join(paras[i] for i in sorted(keep))[:limit]


# ------------------------------------------------------------------ nghiên cứu
@dataclass
class WebSource:
    id: str
    title: str
    url: str
    domain: str
    tier: str
    excerpt: str
    engine: str = ""
    date: str = ""


@dataclass
class WebResearch:
    queries: list[str] = field(default_factory=list)
    sources: list[WebSource] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def context(self) -> str:
        if not self.sources:
            return "(Không lấy được nguồn web" + (f": {'; '.join(self.errors[:3])}" if self.errors else "") + ")"
        return "\n\n".join(f"[{s.id}] {s.title} – {s.domain} ({TIER_VI[s.tier]}{', ' + s.date if s.date else ''})\n"
                           f"URL: {s.url}\n{s.excerpt}" for s in self.sources)

    def markdown(self) -> str:
        if not self.sources:
            return ""
        icon = {"official": "🏛", "trusted": "✅", "other": "⚠️"}
        return "\n".join(f"- [{s.id}] {icon[s.tier]} {s.title} – {s.domain} ({TIER_VI[s.tier]}): {s.url}" for s in self.sources)

    def all_text(self) -> str:
        return "\n".join(f"{s.title}\n{s.excerpt}" for s in self.sources)


def vendor_domains(text: str, cfg: dict) -> list[str]:
    out = []
    for name, doms in cfg["vendors"].items():
        if doms and re.search(r"(?<![\wÀ-ỹ])" + re.escape(name) + r"(?![\wÀ-ỹ])", text, flags=re.I) and doms[0] not in out:
            out.append(doms[0])
    return out


def build_queries(question: str, keywords_en: str = "", cfg: dict | None = None, extra: list[str] | None = None,
                  safe_only_keywords: bool = False) -> list[str]:
    cfg = cfg or load_cfg()
    base = keywords_en.strip() if (safe_only_keywords or not question) else question.strip()
    qs = [base[:200]]
    if keywords_en and not safe_only_keywords:
        qs.append(keywords_en[:200])
    for dom in vendor_domains(f"{question} {keywords_en}", cfg)[:3]:
        qs.append(f"site:{dom} {(keywords_en or base)[:150]}")
    qs += extra or []
    seen, out = set(), []
    for q in qs:
        q = re.sub(r"\s+", " ", q).strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            out.append(q)
    return out[:5]


def research(question: str, keywords_en: str = "", cfg: dict | None = None, get=http_get, log=lambda *_: None,
             extra_queries: list[str] | None = None, safe_only_keywords: bool = False, cache_dir: Path | None = CACHE_DIR,
             start_id: int = 1) -> WebResearch:
    cfg = cfg or load_cfg()
    res = WebResearch()
    if not cfg.get("enabled", True):
        res.errors.append("đã tắt tra web trong config/web_sources.yaml")
        return res
    res.queries = build_queries(question, keywords_en, cfg, extra_queries, safe_only_keywords)
    found: dict[str, Result] = {}

    def run(job):
        eng, q = job
        try:
            return eng, q, ENGINES[eng](q, 8, get=get), None
        except Exception as e:  # mạng chặn / công cụ đổi định dạng
            return eng, q, [], f"{eng}: {type(e).__name__}"

    jobs = [(e, q) for q in res.queries for e in cfg["engines"]
            if e in ENGINES and not (e == "openalex" and q.startswith("site:"))]
    with ThreadPoolExecutor(max_workers=6) as ex:
        for eng, q, items, err in ex.map(run, jobs):
            if err and err not in res.errors:
                res.errors.append(err)
            for r in items:
                found.setdefault(r.url.split("#")[0], r)
    log(f"Tra web: {len(res.queries)} truy vấn → {len(found)} kết quả")
    rank = {"official": 0, "trusted": 1, "other": 2}
    qterms = _terms(f"{question} {keywords_en}")
    cands = sorted(found.values(), key=lambda r: (rank[tier(r.url, cfg)], -len(qterms & _terms(r.title + " " + r.snippet))))
    if not cfg.get("allow_other_domains", True):
        cands = [c for c in cands if tier(c.url, cfg) != "other"]
    picked = cands[: int(cfg["max_pages"])]

    def load(r: Result):
        if r.engine == "openalex":
            return r, r.title, r.snippet, None
        try:
            t, text = fetch_page(r.url, get=get, cache_dir=cache_dir)
            return r, t or r.title, text, None
        except Exception as e:
            return r, r.title, r.snippet, f"{domain_of(r.url)}: {type(e).__name__}"

    with ThreadPoolExecutor(max_workers=5) as ex:
        loaded = list(ex.map(load, picked))
    i = start_id
    for r, title, text, err in loaded:
        if err:
            res.errors.append(err)
        ex_ = best_passages(text, f"{question} {keywords_en}", int(cfg["excerpt_chars"])) if text else r.snippet
        if len(ex_) < 60:
            continue
        res.sources.append(WebSource(f"W{i}", (title or r.title)[:160], r.url, domain_of(r.url), tier(r.url, cfg),
                                     ex_, r.engine, r.date))
        i += 1
    log(f"Đọc {len(res.sources)} trang web làm nguồn")
    return res


# ------------------------------------------------------------------ chống bịa
_STD = re.compile(r"\b(?:IEC|IEEE|ISO|CIGRE\s*TB|TB|UL|NFPA|EN|TCVN|QCVN)\s*(?:TS\s*|TR\s*|Std\.?\s*)?[A-Z]?\d[\d.\-–/]*(?:-\d+)*", re.I)
_NUM = re.compile(r"(?<![\w.])\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\s?(?:%|°C|kV|MVA|MW|MWh|GW|ppm|μL/L|µL/L|pC|USD|EUR|tỷ|triệu|km|năm|giờ|h)\b", re.I)


def _norm(s: str) -> str:
    return re.sub(r"[\s\-–./,]", "", s.lower())


def verify_claims(answer: str, evidence: str, question: str = "") -> list[str]:
    """Số hiệu tiêu chuẩn & số liệu có đơn vị trong câu trả lời mà KHÔNG thấy trong nguồn/câu hỏi."""
    body = answer.split("## Nguồn")[0]
    ev = _norm(evidence + " " + question)
    miss = []
    for m in list(_STD.finditer(body)) + list(_NUM.finditer(body)):
        tok = m.group(0).strip()
        core = _norm(re.sub(r"(?i)^(cigre\s*tb|tb)\s*", "", tok)) if tok.upper().startswith(("CIGRE", "TB")) else _norm(tok)
        num = re.sub(r"[^\d]", "", tok)
        if core and core not in ev and not (num and len(num) >= 3 and num in re.sub(r"[^\d]", " ", evidence).split()):
            if tok not in miss:
                miss.append(tok)
    return miss[:15]


def check_engines(get=http_get) -> list[dict]:
    """Dùng cho nút 'Kiểm tra kết nối web' trong app."""
    out = []
    for name, fn in ENGINES.items():
        t0 = time.time()
        try:
            n = len(fn("transformer online monitoring", 3, get=get))
            out.append({"engine": name, "ok": n > 0, "results": n, "ms": int((time.time() - t0) * 1000)})
        except Exception as e:
            out.append({"engine": name, "ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    try:
        t, text = fetch_page("https://www.iec.ch/homepage", get=get, cache_dir=None)
        out.append({"engine": "đọc trang iec.ch", "ok": bool(text), "results": len(text)})
    except Exception as e:
        out.append({"engine": "đọc trang iec.ch", "ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    return out
