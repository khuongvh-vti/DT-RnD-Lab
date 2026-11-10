"""Kho tri thức local (RAG): đọc PDF/MD/TXT trong library/, chia đoạn, nhúng vector bằng Qwen3-Embedding,
lưu SQLite. Nếu chưa có embedding model, tự rơi về tìm kiếm từ khóa để vẫn chạy được."""
from __future__ import annotations

import hashlib
import math
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SUPPORTED = {".pdf", ".md", ".txt"}


@dataclass
class Hit:
    source: str
    page: int
    text: str
    score: float


def _read_file(path: Path) -> list[tuple[int, str]]:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return [(i + 1, (p.extract_text() or "")) for i, p in enumerate(reader.pages)]
    return [(1, path.read_text(encoding="utf-8", errors="ignore"))]


def chunk(text: str, size: int, overlap: int) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += max(1, size - overlap)
    return [c for c in out if len(c) > 80]


_STOP = set("và của cho các những là có được với trong về này đó thì mà khi để theo từ một như hay hoặc nào gì "
             "không đã đang sẽ rất cũng tại trên dưới ra vào so sánh hệ thống nào phù hợp the of and to in for a an is "
             "on with by as at or be are from that this".split())


def _tokens(s: str) -> list[str]:
    toks = (t.strip(".-") for t in re.findall(r"[\wÀ-ỹ\-\.]+", s.lower()))
    return [t for t in toks if t and t not in _STOP]


class KnowledgeBase:
    def __init__(self, db_path: str, llm=None, chunk_chars=1500, overlap_chars=200):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self.llm = llm
        self.size, self.overlap = chunk_chars, overlap_chars
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS docs(path TEXT PRIMARY KEY, sha TEXT);
        CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, path TEXT, page INT, text TEXT, vec BLOB);
        """)

    # ---------- Ingest ----------
    def ingest(self, library: str, log=print) -> int:
        added = 0
        for path in sorted(Path(library).rglob("*")):
            if path.suffix.lower() not in SUPPORTED or path.name.startswith("README"):
                continue
            sha = hashlib.sha1(path.read_bytes()).hexdigest()
            row = self.db.execute("SELECT sha FROM docs WHERE path=?", (str(path),)).fetchone()
            if row and row[0] == sha:
                # đã nạp; chỉ nạp lại nếu trước đó thiếu embedding mà nay đã có model embedding
                missing = self.db.execute("SELECT COUNT(*) FROM chunks WHERE path=? AND vec IS NULL", (str(path),)).fetchone()[0]
                if not (missing and self.llm is not None and self._embed(["ping"])[0] is not None):
                    continue
            self.db.execute("DELETE FROM chunks WHERE path=?", (str(path),))
            pages = _read_file(path)
            head = next((ln[2:].strip() for _, t in pages[:1] for ln in t.splitlines() if ln.startswith("# ")), path.stem)
            # gắn tiêu đề tài liệu vào mỗi đoạn để tìm kiếm & trích dẫn không mất ngữ cảnh (đoạn giữa file)
            pieces = [(pg, c if c.lstrip().startswith("# ") else f"[{head}]\n{c}")
                      for pg, t in pages for c in chunk(t, self.size, self.overlap)]
            vecs = self._embed([c for _, c in pieces])
            for (pg, c), v in zip(pieces, vecs):
                blob = None if v is None else np.asarray(v, dtype=np.float32).tobytes()
                self.db.execute("INSERT INTO chunks(path,page,text,vec) VALUES(?,?,?,?)", (str(path), pg, c, blob))
            self.db.execute("INSERT OR REPLACE INTO docs VALUES(?,?)", (str(path), sha))
            self.db.commit()
            added += len(pieces)
            log(f"  + {path} ({len(pieces)} đoạn)")
        return added

    def _embed(self, texts: list[str]):
        if not texts:
            return []
        if self.llm is None:
            return [None] * len(texts)
        try:
            out = []
            for i in range(0, len(texts), 32):
                out.extend(self.llm.embed(texts[i:i + 32]))
            return out
        except Exception:
            return [None] * len(texts)

    def stats(self) -> dict:
        n_docs = self.db.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
        n_chunks = self.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return {"documents": n_docs, "chunks": n_chunks}

    # ---------- Search ----------
    def _tokcache(self, rows):
        """Token hóa mỗi đoạn một lần (cache theo số đoạn) – kho lớn (tiêu chuẩn hàng nghìn trang) vẫn tìm nhanh."""
        key = (len(rows), rows[-1][2][:50] if rows else "")
        if getattr(self, "_tc_key", None) != key:
            docs = [_tokens(r[2]) for r in rows]
            sets = [set(d) for d in docs]
            titles = [set(_tokens(r[2].lstrip().split("\n", 1)[0])) for r in rows]
            df = Counter(w for st in sets for w in st)
            self._tc_key, self._tc = key, (docs, sets, titles, df)
        return self._tc

    def search(self, query: str, k: int = 8) -> list[Hit]:
        rows = self.db.execute("SELECT path,page,text,vec FROM chunks").fetchall()
        if not rows:
            return []
        docs, sets, titles, df = self._tokcache(rows)
        qv = None
        if self.llm is not None and any(r[3] for r in rows):
            try:
                qv = np.asarray(self.llm.embed([query])[0], dtype=np.float32)
            except Exception:
                qv = None
        scored = []  # (score, idx)
        if qv is not None:
            qn = qv / (np.linalg.norm(qv) + 1e-9)
            for i, r in enumerate(rows):
                if r[3]:
                    vv = np.frombuffer(r[3], dtype=np.float32)
                    scored.append((float(qn @ (vv / (np.linalg.norm(vv) + 1e-9))), i))
        else:  # fallback: BM25 đơn giản
            avg = sum(map(len, docs)) / len(docs)
            q = _tokens(query)
            n = len(docs)
            for i, d in enumerate(docs):
                if not any(w in sets[i] for w in q):
                    continue
                tf = Counter(d)
                s = sum(math.log(1 + n / (1 + df[w])) * tf[w] * 2.2 /
                        (tf[w] + 1.2 * (0.25 + 0.75 * len(d) / avg)) for w in q if w in tf)
                scored.append((s, i))
        scored.sort(key=lambda x: -x[0])
        top = [x for x in scored[:k] if x[0] > 0]
        # Bảo đảm bao phủ thực thể: câu hỏi so sánh "Siemens và Hitachi" phải có đoạn cho CẢ HAI tên riêng hiếm
        toks = [w for w in dict.fromkeys(_tokens(query)) if len(w) > 2]
        for w in toks:
            if not df.get(w) or df[w] > 0.3 * len(rows):
                continue
            if any(w in titles[i] for _, i in top):
                continue
            best = next((x for x in scored if w in titles[x[1]]), None)
            if best is None and any(w in sets[i] for _, i in top):
                continue
            best = best or next((x for x in scored if w in sets[x[1]]), None)
            if best is None:  # đoạn có từ khóa nhưng không được chấm điểm (ví dụ chỉ có embedding)
                idx = next((i for i in range(len(rows)) if w in titles[i]), None)
                best = (0.0, idx) if idx is not None else None
            if best is not None and best not in top:
                if len(top) >= k:
                    top.pop()
                top.append(best)
        return [Hit(rows[i][0], rows[i][1], rows[i][2], s) for s, i in top]


def format_context(hits: list[Hit]) -> str:
    if not hits:
        return "(Kho tài liệu chưa có tài liệu liên quan – hãy ghi rõ các nhận định là GIẢ ĐỊNH.)"
    return "\n\n".join(f"[S{i}] {Path(h.source).name}, trang {h.page}:\n{h.text}" for i, h in enumerate(hits, 1))
