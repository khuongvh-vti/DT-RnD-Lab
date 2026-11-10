#!/bin/bash
# Cai dat chay tu dong tren macOS:
#  1) Server VTI R&D Lab luon chay (http://localhost:8766) khi dang nhap
#  2) Server tu chay chu ky bao cao 3 ngay/lan cho cac module dang hoat dong
# Chay: bash scripts/install_app.sh   |  Go: bash scripts/install_app.sh --uninstall
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="$DIR/.venv/bin/python3"; [ -x "$PY" ] || PY="$(command -v python3)"
LA="$HOME/Library/LaunchAgents"; mkdir -p "$LA" "$DIR/logs"
if [ "$1" = "--uninstall" ]; then
  for n in server weekly; do launchctl unload "$LA/com.vticorp.dtlab.$n.plist" 2>/dev/null || true; rm -f "$LA/com.vticorp.dtlab.$n.plist"; done
  echo "Da go server + lich tuan."; exit 0
fi
cat > "$LA/com.vticorp.dtlab.server.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.vticorp.dtlab.server</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$DIR/app/server.py</string></array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$DIR/logs/server.log</string>
  <key>StandardErrorPath</key><string>$DIR/logs/server.log</string>
</dict></plist>
PL
# Lich tuan cu duoc thay bang chu ky 3 ngay do chinh server tu chay (config/settings.yaml -> cycle)
launchctl unload "$LA/com.vticorp.dtlab.weekly.plist" 2>/dev/null || true; rm -f "$LA/com.vticorp.dtlab.weekly.plist"
launchctl unload "$LA/com.vticorp.dtlab.server.plist" 2>/dev/null || true; launchctl load "$LA/com.vticorp.dtlab.server.plist"
echo "Da cai: server luon chay tai http://localhost:8766; bao cao nghien cuu tu chay moi 3 ngay sau 07:00 (khi Ollama dang chay)."
