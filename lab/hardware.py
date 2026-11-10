"""Nhận biết RAM máy và chọn model Qwen phù hợp (Apple Silicon dùng unified memory)."""
from __future__ import annotations

import platform
import subprocess

# (RAM tối thiểu GB, model, ghi chú) – tag theo thư viện Ollama, kiểm tra lại bằng `ollama list`
QWEN_LADDER = [
    (48, "qwen3.6:35b-a3b", "MoE ~3B active: nhanh, chất lượng cao; ~23 GB"),
    (32, "qwen3.6:27b", "dense 27B, mạnh nhất cho máy 32 GB; ~18 GB"),
    (16, "qwen3.5:9b", "điểm cân bằng cho 16–24 GB; ~6.6 GB"),
    (8, "qwen3.5:4b", "máy 8 GB; chất lượng vừa phải"),
    (0, "qwen3.5:2b", "chỉ để thử"),
]


def total_ram_gb() -> float:
    try:
        if platform.system() == "Darwin":
            b = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
            return b / 1024 ** 3
        with open("/proc/meminfo") as f:
            kb = int(f.readline().split()[1])
            return kb / 1024 ** 2
    except Exception:
        return 0.0


def recommend_model(ram_gb: float | None = None) -> tuple[str, str]:
    ram = total_ram_gb() if ram_gb is None else ram_gb
    for min_gb, model, note in QWEN_LADDER:
        if ram >= min_gb:
            return model, note
    return QWEN_LADDER[-1][1], QWEN_LADDER[-1][2]
