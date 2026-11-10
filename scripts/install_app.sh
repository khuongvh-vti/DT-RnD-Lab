#!/bin/bash
# Cai dat chay tu dong tren macOS:
#  1) Server DT-RnD-Lab luon chay (http://localhost:8766) khi dang nhap
#  2) Vong nghien cuu tuan luc 08:00 sang thu Hai (neu Mac ngu, se chay khi thuc day)
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
cat > "$LA/com.vticorp.dtlab.weekly.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.vticorp.dtlab.weekly</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$DIR/scripts/run_weekly.sh</string></array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>StartCalendarInterval</key><dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$DIR/logs/weekly.log</string>
  <key>StandardErrorPath</key><string>$DIR/logs/weekly.log</string>
</dict></plist>
PL
for n in server weekly; do launchctl unload "$LA/com.vticorp.dtlab.$n.plist" 2>/dev/null || true; launchctl load "$LA/com.vticorp.dtlab.$n.plist"; done
echo "Da cai: server luon chay tai http://localhost:8766 + vong nghien cuu 08:00 thu Hai."
