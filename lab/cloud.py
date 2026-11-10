"""Model cloud lớn (OpenAI-compatible: Alibaba Model Studio/DashScope Qwen-Max, OpenRouter…) và bộ định tuyến hybrid.

Nguyên tắc an toàn dữ liệu:
- Embedding và kho tài liệu LUÔN ở máy local.
- Một yêu cầu bị buộc chạy local nếu ngữ cảnh chứa đoạn trích từ thư mục nhạy cảm (mặc định library/06_vti_data)
  hoặc khi vượt ngân sách tháng, hoặc khi chưa có API key.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path


class OpenAICompatClient:
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float = 0.3, timeout_s: int = 600):
        self.base_url, self.api_key, self.model = base_url.rstrip("/"), api_key, model
        self.temperature, self.timeout_s = temperature, timeout_s
        self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0}

    def chat(self, system: str, user: str, **_) -> str:
        body = {"model": self.model, "temperature": self.temperature,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        req = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {self.api_key}"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
            out = json.loads(r.read().decode("utf-8"))
        self.last_usage = out.get("usage", self.last_usage)
        text = out["choices"][0]["message"]["content"] or ""
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


class UsageLedger:
    """Ghi token & chi phí ước tính theo tháng vào data/cloud_usage.json."""

    def __init__(self, path: str, price_in: float, price_out: float):
        self.path, self.price_in, self.price_out = Path(path), price_in, price_out

    def _load(self) -> dict:
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def month_cost(self) -> float:
        return self._load().get(dt.date.today().strftime("%Y-%m"), {}).get("usd", 0.0)

    def add(self, usage: dict, role: str):
        data, key = self._load(), dt.date.today().strftime("%Y-%m")
        m = data.setdefault(key, {"usd": 0.0, "in": 0, "out": 0, "calls": 0, "by_role": {}})
        pi, po = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        usd = pi / 1e6 * self.price_in + po / 1e6 * self.price_out
        m["usd"] += usd; m["in"] += pi; m["out"] += po; m["calls"] += 1
        m["by_role"][role] = m["by_role"].get(role, 0.0) + usd
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2))


class HybridLLM:
    """Giao diện giống OllamaClient (chat/chat_json/embed) nhưng chọn local hoặc cloud theo vai trò."""

    def __init__(self, local, cloud_cfg: dict, data_dir: str, log=print):
        self.local, self.cfg, self.log = local, cloud_cfg or {}, log
        self.cloud = None
        key = os.environ.get(self.cfg.get("api_key_env", "DASHSCOPE_API_KEY"), "")
        if self.cfg.get("enabled") and key:
            self.cloud = OpenAICompatClient(self.cfg["base_url"], key, self.cfg["model"],
                                            self.cfg.get("temperature", 0.3))
        self.ledger = UsageLedger(str(Path(data_dir) / "cloud_usage.json"),
                                  self.cfg.get("price_in_per_m", 1.2), self.cfg.get("price_out_per_m", 6.0))
        self.chat_model = getattr(local, "chat_model", "local")
        self.embed_model = getattr(local, "embed_model", "")

    def route(self, role: str, sensitive: bool) -> str:
        if self.cloud is None or sensitive or role not in self.cfg.get("roles", []):
            return "local"
        if self.ledger.month_cost() >= self.cfg.get("monthly_budget_usd", 10):
            self.log("! Đã chạm ngân sách cloud tháng này → chạy local")
            return "local"
        return "cloud"

    def chat(self, system: str, user: str, role: str = "default", sensitive: bool = False, **kw) -> str:
        if self.route(role, sensitive) == "cloud":
            try:
                text = self.cloud.chat(system, user)
                self.ledger.add(self.cloud.last_usage, role)
                return text
            except (urllib.error.URLError, KeyError, TimeoutError) as e:
                self.log(f"! Cloud lỗi ({e}) → chuyển local")
        return self.local.chat(system, user, **kw)

    def chat_json(self, system: str, user: str, role: str = "default", sensitive: bool = False):
        raw = self.chat(system, user + "\n\nChỉ trả về JSON hợp lệ, không giải thích.", role, sensitive)
        m = re.search(r"(\{.*\}|\[.*\])", raw, flags=re.S)
        if not m:
            raise ValueError(f"Model không trả JSON: {raw[:300]}")
        return json.loads(m.group(1))

    def embed(self, texts):
        return self.local.embed(texts)  # embedding luôn local

    def list_models(self):
        return self.local.list_models()


def is_sensitive(sources: list[str], sensitive_paths: list[str]) -> bool:
    norm = [p.replace("\\", "/").rstrip("/") for p in sensitive_paths]
    return any(any(n in s.replace("\\", "/") for n in norm) for s in sources)
