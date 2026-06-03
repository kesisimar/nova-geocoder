#!/usr/bin/env bash
set -euo pipefail

echo "Καλώς ήρθατε στο Greek Geocoder!"

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Έλεγχος για Homebrew..."
BREW_CMD=""
if [ -x "/opt/homebrew/bin/brew" ]; then
  BREW_CMD="/opt/homebrew/bin/brew"
elif [ -x "/usr/local/bin/brew" ]; then
  BREW_CMD="/usr/local/bin/brew"
fi

if [ -z "$BREW_CMD" ]; then
  echo "Το Homebrew δεν βρέθηκε. Θα εγκατασταθεί τώρα..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -x "/opt/homebrew/bin/brew" ]; then
    BREW_CMD="/opt/homebrew/bin/brew"
  elif [ -x "/usr/local/bin/brew" ]; then
    BREW_CMD="/usr/local/bin/brew"
  fi
fi

if [ -n "$BREW_CMD" ]; then
  echo "Homebrew βρέθηκε: $BREW_CMD"
  eval "$("$BREW_CMD" shellenv)"
fi

echo "Εγκατάσταση / Έλεγχος tcl-tk..."
if ! "$BREW_CMD" list tcl-tk >/dev/null 2>&1; then
  "$BREW_CMD" install tcl-tk
fi

export TK_SILENCE_DEPRECATION=1

echo "Έλεγχος για Python3..."
PYTHON_CMD=""
if [ -x "/usr/bin/python3" ] && /usr/bin/python3 -c "import tkinter" >/dev/null 2>&1; then
  PYTHON_CMD="/usr/bin/python3"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import tkinter" >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
elif [ -n "$BREW_CMD" ] && [ -x "$($BREW_CMD --prefix)/bin/python3" ] && "$($BREW_CMD --prefix)/bin/python3" -c "import tkinter" >/dev/null 2>&1; then
  PYTHON_CMD="$($BREW_CMD --prefix)/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
fi

if [ -z "$PYTHON_CMD" ]; then
  echo "Python3 δεν βρέθηκε. Θα εγκατασταθεί μέσω Homebrew..."
  "$BREW_CMD" install python
  PYTHON_CMD="$($BREW_CMD --prefix)/bin/python3"
fi

echo "Χρησιμοποιώντας Python: $PYTHON_CMD"

echo "Δημιουργία virtual environment (venv)..."
"$PYTHON_CMD" -m venv "$PROJECT_DIR/venv"
source "$PROJECT_DIR/venv/bin/activate"

echo "Εγκατάσταση απαιτήσεων..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "Εκκίνηση εφαρμογής..."
python "$PROJECT_DIR/main.py"

# Make script executable for future runs
chmod +x "$0" || true
