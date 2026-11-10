#!/bin/bash
# Nhap dup de mo DT-RnD-Lab tren Chrome.
# Lan dau: tu tao moi truong Python (.venv) va cai thu vien (~1 phut, can Internet).
cd "$(dirname "$0")"
echo "=== VTI R&D Lab (DT-RnD-Lab) ==="
if ! command -v python3 >/dev/null; then
  echo "May chua co Python 3. Cai bang lenh: xcode-select --install  (roi nhap dup lai file nay)"; read -n1 -p "Nhan phim bat ky de dong..."; exit 1
fi
if [ ! -x .venv/bin/python3 ]; then
  echo "Lan dau chay: dang tao moi truong Python va cai thu vien, vui long doi..."
  python3 -m venv .venv && .venv/bin/python3 -m pip install -q --upgrade pip && .venv/bin/python3 -m pip install -q -r requirements.txt \
    || { echo "Cai thu vien loi - kiem tra Internet roi thu lai."; read -n1 -p "Nhan phim bat ky de dong..."; exit 1; }
fi
mkdir -p logs data
if command -v ollama >/dev/null; then
  pgrep -x ollama >/dev/null || pgrep -f "Ollama" >/dev/null || (nohup ollama serve >/tmp/ollama.log 2>&1 &)
else
  echo "Chua cai Ollama (Qwen local). App van mo duoc; cai Ollama tai https://ollama.com/download de hoi dap."
fi
# Server dang chay ban cu (khong co tinh nang "modules") -> tat de bat lai ban moi
if curl -s -m 2 http://localhost:8766/api/health | grep -qv '"modules"'; then
  echo "Server dang chay ban cu - khoi dong lai..."
  pkill -f "app/server.py" 2>/dev/null; sleep 2
fi
if ! curl -s -m 2 http://localhost:8766/api/health >/dev/null; then
  echo "Dang bat server..."
  nohup .venv/bin/python3 app/server.py >logs/server.log 2>&1 &
  for i in $(seq 1 15); do curl -s -m 1 http://localhost:8766/api/health >/dev/null && break; sleep 1; done
fi
if curl -s -m 2 http://localhost:8766/api/health >/dev/null; then
  open -a "Google Chrome" http://localhost:8766 || open http://localhost:8766
  echo "Da mo http://localhost:8766 - co the dong cua so Terminal nay."
else
  echo "Server khong chay duoc. Loi:"; tail -20 logs/server.log; read -n1 -p "Nhan phim bat ky de dong..."
fi
