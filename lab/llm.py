"""Ollama client tối giản (chỉ dùng thư viện chuẩn) – mọi thứ chạy local trên máy anh."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request


class LLMError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, host: str, chat_model: str, embed_model: str,
                 temperature: float = 0.3, num_ctx: int = 32768, timeout_s: int = 900):
        self.host = host.rstrip("/")
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.timeout_s = timeout_s

    # ---------- HTTP ----------
    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            self.host + path, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.URLError as e:  # pragma: no cover - cần Ollama thật
            raise LLMError(f"Không gọi được Ollama tại {self.host}{path}: {e}. "
                           "Kiểm tra `ollama serve` đang chạy.") from e

    def list_models(self) -> list[str]:
        try:
            with urllib.request.urlopen(self.host + "/api/tags", timeout=10) as r:
                return [m["name"] for m in json.loads(r.read())["models"]]
        except Exception:
            return []

    # ---------- Chat ----------
    def chat(self, system: str, user: str, think: bool = False, **_) -> str:
        body = {
            "model": self.chat_model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "stream": False,
            "think": think,
            "options": {"temperature": self.temperature, "num_ctx": self.num_ctx},
        }
        out = self._post("/api/chat", body)
        text = out.get("message", {}).get("content", "")
        # Một số model Qwen trả cả khối <think>…</think>; bỏ đi cho báo cáo gọn
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()

    def chat_json(self, system: str, user: str, **_):
        raw = self.chat(system, user + "\n\nChỉ trả về JSON hợp lệ, không giải thích.")
        m = re.search(r"(\{.*\}|\[.*\])", raw, flags=re.S)
        if not m:
            raise LLMError(f"Model không trả JSON: {raw[:300]}")
        return json.loads(m.group(1))

    # ---------- Embeddings ----------
    def embed(self, texts: list[str]) -> list[list[float]]:
        out = self._post("/api/embed", {"model": self.embed_model, "input": texts})
        return out["embeddings"]
