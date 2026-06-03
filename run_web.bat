@echo off
REM Run the Flask web app on Windows. Creates venv and installs deps if missing.
if not exist ".venv\Scripts\activate" (
    python -m venv .venv
    call .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)
REM Launch the server in a new terminal window so this script can return.
start "" /min cmd /k "call .venv\Scripts\activate && set TK_SILENCE_DEPRECATION=1 && python web_app.py"
REM Open Chrome to the app (non-blocking)
start "" "chrome" "http://127.0.0.1:5000"
