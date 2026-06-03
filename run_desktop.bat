@echo off
REM Run the desktop tkinter app on Windows. Creates venv and installs deps if missing.
if not exist ".venv\Scripts\activate" (
    python -m venv .venv
    call .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)
call .venv\Scripts\activate
set TK_SILENCE_DEPRECATION=1
python main.py
