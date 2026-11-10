#!/usr/bin/env bash
# Chạy tay một chu kỳ nghiên cứu (mọi module đang hoạt động). Bình thường server tự chạy mỗi 3 ngày.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
pgrep -x ollama >/dev/null || (ollama serve >/tmp/ollama.log 2>&1 &) ; sleep 3
python3 dtlab.py ingest
python3 dtlab.py cycle --focus "${1:-}" >> logs/cycle.log 2>&1
