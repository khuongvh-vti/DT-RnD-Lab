"""Cloud model chain – ưu tiên MIỄN PHÍ, xoay vòng để khai thác tối đa quota, cuối cùng mới đến trả phí / local.

Thứ tự mặc định (config/settings.yaml → cloud.providers):
  1. Alibaba Model Studio (Singapore): mỗi model Qwen có quota miễn phí riêng (≈1M token, 90 ngày) → xoay vòng
     qua nhiều model, model nào gần hết quota thì chuyển model kế tiếp.
  2. OpenRouter các model ':free' (giới hạn ~20 req/phút, 50 req/ngày; 1.000 req/ngày nếu từng nạp ≥10 USD).
  3. (tùy chọn) model trả phí, chỉ khi allow_paid: true và còn ngân sách tháng.
  4. Local Ollama (qwen3.5:9b) – luôn là phương án cuối, và là bắt buộc với dữ liệu nhạy cảm.

An toàn dữ liệu: embedding/kho tài liệu luôn local; ngữ cảnh có trích đoạn từ sensitive_paths → chỉ chạy local.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path


class QuotaExceeded(RuntimeError):
    pass


class OpenAICompatClient:
    def __init__(self, base_url: str, api_key: str, temperature: float = 0.3, timeout_s: int = 600,
                 extra_headers: dict | None = None):
        self.base_url, self.api_key = base_url.rstrip("/"), api_key
        self.temperature, self.timeout_s = temperature, timeout_s
        self.extra_headers = extra_headers or {}

    def chat(self, model: str, system: str, user: str) -> tuple[str, dict]:
        body = {"model": model, "temperature": self.temperature,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}",
                   **self.extra_headers}
        req = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body).encode(),
                                     headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                out = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (402, 403, 429):  # hết quota / hết lượt / cần thanh toán
                raise QuotaExceeded(f"{model}: HTTP {e.code}") from e
            raise
        text = out["choices"][0]["message"]["content"] or ""
        usage = out.get("usage") or {}
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip(), usage


class Ledger:
    """Theo dõi token theo model (cho quota trọn đời) + số request theo ngày (cho giới hạn ngày) + chi phí tháng."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def tokens(self, provider: str, model: str) -> int:
        return self.data.get("tokens", {}).get(f"{provider}/{model}", 0)

    def requests_today(self, provider: str) -> int:
        return self.data.get("daily", {}).get(dt.date.today().isoformat(), {}).get(provider, 0)

    def blocked_today(self, provider: str, model: str) -> bool:
        return f"{provider}/{model}" in self.data.get("blocked", {}).get(dt.date.today().isoformat(), [])

    def block_today(self, provider: str, model: str):
        self.data.setdefault("blocked", {}).setdefault(dt.date.today().isoformat(), []).append(f"{provider}/{model}")
        self.save()

    def month_cost(self) -> float:
        return self.data.get("cost", {}).get(dt.date.today().strftime("%Y-%m"), 0.0)

    def add(self, provider: str, model: str, usage: dict, role: str, usd: float):
        tot = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
        k = f"{provider}/{model}"
        self.data.setdefault("tokens", {})[k] = self.tokens(provider, model) + tot
        day = self.data.setdefault("daily", {}).setdefault(dt.date.today().isoformat(), {})
        day[provider] = day.get(provider, 0) + 1
        m = dt.date.today().strftime("%Y-%m")
        self.data.setdefault("cost", {})[m] = self.month_cost() + usd
        self.data.setdefault("by_role", {}).setdefault(m, {})
        self.data["by_role"][m][role] = self.data["by_role"][m].get(role, 0) + tot
        self.save()


class HybridLLM:
    """Giao diện như OllamaClient. Chọn engine: free cloud → (paid cloud) → local."""

    def __init__(self, local, cloud_cfg: dict, data_dir: str, log=print):
        self.local, self.cfg, self.log = local, cloud_cfg or {}, log
        self.ledger = Ledger(str(Path(data_dir) / "cloud_usage.json"))
        self.chat_model = getattr(local, "chat_model", "local")
        self.embed_model = getattr(local, "embed_model", "")
        self.providers = []
        if self.cfg.get("enabled"):
            for p in self.cfg.get("providers", []):
                key = os.environ.get(p.get("api_key_env", ""), "")
                if not key or (p.get("paid") and not self.cfg.get("allow_paid")):
                    continue
                if p.get("expires") and dt.date.today().isoformat() > str(p["expires"]):
                    continue
                client = OpenAICompatClient(p["base_url"], key, self.cfg.get("temperature", 0.3),
                                            extra_headers=p.get("headers"))
                self.providers.append((p, client))
        self.last_engine = "local"

    @property
    def cloud(self):  # tương thích: có ít nhất 1 provider cloud dùng được
        return self.providers or None

    def _candidates(self):
        for p, client in self.providers:
            if p.get("daily_requests") and self.ledger.requests_today(p["name"]) >= p["daily_requests"]:
                continue
            if p.get("paid") and self.ledger.month_cost() >= self.cfg.get("monthly_budget_usd", 0):
                continue
            for model in p["models"]:
                quota = p.get("token_quota_per_model")
                if quota and self.ledger.tokens(p["name"], model) >= quota * p.get("quota_safety", 0.9):
                    continue
                if self.ledger.blocked_today(p["name"], model):
                    continue
                yield p, client, model

    def route(self, role: str, sensitive: bool) -> str:
        if sensitive or role not in self.cfg.get("roles", []):
            return "local"
        for p, _, model in self._candidates():
            return f"{p['name']}/{model}"
        return "local"

    def chat(self, system: str, user: str, role: str = "default", sensitive: bool = False, **kw) -> str:
        if not sensitive and role in self.cfg.get("roles", []):
            for p, client, model in self._candidates():
                try:
                    text, usage = client.chat(model, system, user)
                    usd = 0.0
                    if p.get("paid"):
                        usd = (usage.get("prompt_tokens", 0) * p.get("price_in_per_m", 0)
                               + usage.get("completion_tokens", 0) * p.get("price_out_per_m", 0)) / 1e6
                    self.ledger.add(p["name"], model, usage, role, usd)
                    self.last_engine = f"{p['name']}/{model}"
                    return text
                except QuotaExceeded as e:
                    self.log(f"  · {e} → thử model/provider kế tiếp")
                    self.ledger.block_today(p["name"], model)
                except (urllib.error.URLError, KeyError, TimeoutError, json.JSONDecodeError) as e:
                    self.log(f"  · {p['name']}/{model} lỗi ({e}) → thử tiếp")
        self.last_engine = f"local/{self.chat_model}"
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

    def status(self) -> list[str]:
        lines = []
        for p, _ in self.providers:
            for m in p["models"]:
                used = self.ledger.tokens(p["name"], m)
                q = p.get("token_quota_per_model")
                lines.append(f"  {p['name']}/{m}: {used:,} token" + (f" / {q:,} quota" if q else "")
                             + (" (trả phí)" if p.get("paid") else " (miễn phí)"))
            if p.get("daily_requests"):
                lines.append(f"  {p['name']}: {self.ledger.requests_today(p['name'])}/{p['daily_requests']} request hôm nay")
        return lines


def is_sensitive(sources: list[str], sensitive_paths: list[str]) -> bool:
    norm = [p.replace("\\", "/").rstrip("/") for p in sensitive_paths]
    return any(any(n in s.replace("\\", "/") for n in norm) for s in sources)
