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


def _tokens(s: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ\-\.]+", s.lower())


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
                continue
            self.db.execute("DELETE FROM chunks WHERE path=?", (str(path),))
            pieces = [(pg, c) for pg, t in _read_file(path) for c in chunk(t, self.size, self.overlap)]
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
    def search(self, query: str, k: int = 8) -> list[Hit]:
        rows = self.db.execute("SELECT path,page,text,vec FROM chunks").fetchall()
        if not rows:
            return []
        qv = None
        if self.llm is not None and any(r[3] for r in rows):
            try:
                qv = np.asarray(self.llm.embed([query])[0], dtype=np.float32)
            except Exception:
                qv = None
        scored = []
        if qv is not None:
            qn = qv / (np.linalg.norm(qv) + 1e-9)
            for p, pg, t, v in rows:
                if v:
                    vv = np.frombuffer(v, dtype=np.float32)
                    scored.append((float(qn @ (vv / (np.linalg.norm(vv) + 1e-9))), p, pg, t))
        else:  # fallback: BM25 đơn giản
            docs = [_tokens(r[2]) for r in rows]
            df = Counter(w for d in docs for w in set(d))
            avg = sum(map(len, docs)) / len(docs)
            q = _tokens(query)
            for (p, pg, t, _), d in zip(rows, docs):
                tf = Counter(d)
                s = sum(math.log(1 + len(docs) / (1 + df[w])) * tf[w] * 2.2 /
                        (tf[w] + 1.2 * (0.25 + 0.75 * len(d) / avg)) for w in q if w in tf)
                scored.append((s, p, pg, t))
        scored.sort(key=lambda x: -x[0])
        return [Hit(p, pg, t, s) for s, p, pg, t in scored[:k] if s > 0]


def format_context(hits: list[Hit]) -> str:
    if not hits:
        return "(Kho tài liệu chưa có tài liệu liên quan – hãy ghi rõ các nhận định là GIẢ ĐỊNH.)"
    return "\n\n".join(f"[S{i}] {Path(h.source).name}, trang {h.page}:\n{h.text}" for i, h in enumerate(hits, 1))
