#!/usr/bin/env bash
# Cài đặt Phòng R&D Digital Twin trên macOS (Apple Silicon). Chạy: bash scripts/install_mac.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ollama >/dev/null 2>&1; then
  echo "Chưa có Ollama. Tải tại https://ollama.com/download (hoặc: brew install ollama) rồi chạy lại."; exit 1
fi
pgrep -x ollama >/dev/null || (ollama serve >/tmp/ollama.log 2>&1 &) ; sleep 2

python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt

python3 dtlab.py doctor
python3 dtlab.py setup      # tải model Qwen phù hợp RAM + qwen3-embedding
python3 dtlab.py ingest     # nạp tài liệu trong library/
python3 -m pytest -q tests

echo "Xong. Thử: source .venv/bin/activate && python3 dtlab.py ask \"Mô hình nhiệt IEC 60076-7 cần dữ liệu gì?\""
