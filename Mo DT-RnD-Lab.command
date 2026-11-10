#!/bin/bash
# Nhap dup de mo DT-RnD-Lab tren Chrome (tu bat server neu chua chay)
cd "$(dirname "$0")"
PY=python3; [ -x .venv/bin/python3 ] && PY=.venv/bin/python3
mkdir -p logs
pgrep -x ollama >/dev/null || (command -v ollama >/dev/null && (nohup ollama serve >/tmp/ollama.log 2>&1 &))
curl -s -m 2 http://localhost:8766/api/health >/dev/null || (nohup $PY app/server.py >logs/server.log 2>&1 &)
for i in 1 2 3 4 5 6; do curl -s -m 1 http://localhost:8766/api/health >/dev/null && break; sleep 1; done
open -a "Google Chrome" http://localhost:8766 || open http://localhost:8766
