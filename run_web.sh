#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJECT_DIR/.venv"

if [ ! -d "$VENV" ]; then
  echo "Virtualenv not found at $VENV. Create it first or run install script."
  exit 1
fi

source "$VENV/bin/activate"

echo "Starting web app..."
nohup python "$PROJECT_DIR/web_app.py" > "$PROJECT_DIR/web.log" 2>&1 &
sleep 0.5

echo "Opening Google Chrome at http://127.0.0.1:5000"
open -a "Google Chrome" "http://127.0.0.1:5000" || open "http://127.0.0.1:5000"

echo "Logs: $PROJECT_DIR/web.log"
echo "To stop the server: pkill -f web_app.py || kill $(cat $PROJECT_DIR/web.pid 2>/dev/null)"
