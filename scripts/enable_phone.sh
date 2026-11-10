#!/bin/bash
# Bat/tat truy cap DT-RnD-Lab tu dien thoai. Chay: bash scripts/enable_phone.sh   |  Tat: bash scripts/enable_phone.sh --off
cd "$(dirname "$0")/.."
mkdir -p data
if [ "$1" = "--off" ]; then
  rm -f data/remote.json 2>/dev/null || echo '{}' > data/remote.json
  echo "Da tat truy cap tu may khac. Khoi dong lai server de ap dung."
else
  [ -f data/remote.json ] && TOKEN=$(python3 -c "import json;print(json.load(open('data/remote.json')).get('token',''))" 2>/dev/null)
  [ -z "$TOKEN" ] && TOKEN=$(python3 -c "import secrets;print(secrets.token_urlsafe(9))")
  echo "{\"token\": \"$TOKEN\"}" > data/remote.json
  NAME=$(scutil --get LocalHostName 2>/dev/null || hostname -s)
  IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
  TS=$(command -v tailscale >/dev/null && tailscale ip -4 2>/dev/null | head -1)
  echo ""
  echo "=== Mo tren dien thoai (cung mang Wi-Fi voi Mac) ==="
  echo "  http://$NAME.local:8766/?key=$TOKEN"
  [ -n "$IP" ] && echo "  hoac: http://$IP:8766/?key=$TOKEN"
  [ -n "$TS" ] && echo "=== Qua Tailscale (o bat ky dau) ===" && echo "  http://$TS:8766/?key=$TOKEN"
  echo ""
  echo "Ma truy cap: $TOKEN  (giu bi mat; chi can mo link 1 lan, dien thoai se nho)"
fi
# khoi dong lai server
if launchctl list 2>/dev/null | grep -q com.vticorp.dtlab.server; then
  launchctl kickstart -k gui/$(id -u)/com.vticorp.dtlab.server
else
  pkill -f app/server.py; sleep 1
  PY=python3; [ -x .venv/bin/python3 ] && PY=.venv/bin/python3
  mkdir -p logs; nohup $PY app/server.py > logs/server.log 2>&1 &
fi
echo "Server da khoi dong lai."
