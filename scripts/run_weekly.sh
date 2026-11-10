#!/usr/bin/env bash
# Chạy vòng nghiên cứu tuần (launchd gọi script này 8:00 sáng thứ Hai).
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
pgrep -x ollama >/dev/null || (ollama serve >/tmp/ollama.log 2>&1 &) ; sleep 3
python3 dtlab.py ingest
python3 dtlab.py week --focus "${1:-}" >> logs/weekly.log 2>&1
