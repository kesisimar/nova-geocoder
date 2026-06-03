#!/usr/bin/env bash
set -euo pipefail

# Helper script to create a virtualenv, install requirements, and run the app
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

# Prefer Homebrew Python if available on macOS
BREW_CMD=""
if [ -x "/opt/homebrew/bin/brew" ]; then
  BREW_CMD="/opt/homebrew/bin/brew"
elif [ -x "/usr/local/bin/brew" ]; then
  BREW_CMD="/usr/local/bin/brew"
fi

if [ -n "$BREW_CMD" ]; then
  eval "$("$BREW_CMD" shellenv)"
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR..."
  PYTHON_CMD=""
  if [ -x "/usr/bin/python3" ] && /usr/bin/python3 -c "import tkinter" >/dev/null 2>&1; then
    PYTHON_CMD="/usr/bin/python3"
  elif command -v python3 >/dev/null 2>&1 && python3 -c "import tkinter" >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python3)"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python)"
  fi

  if [ -z "$PYTHON_CMD" ]; then
    echo "Δεν βρέθηκε Python για το virtualenv. Χρησιμοποιήστε κανονικό python3." >&2
    exit 1
  fi

  "$PYTHON_CMD" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  echo "Installing requirements..."
  "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
fi

export TK_SILENCE_DEPRECATION=1

echo "Running app..."
"$VENV_DIR/bin/python" "$PROJECT_DIR/main.py"
