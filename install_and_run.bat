@echo off
chcp 65001 >nul
echo Καλώς ήρθατε στο Greek Geocoder!

REM Check for Python
where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo ΣΦΑΛΜΑ: Η Python δεν είναι εγκατεστημένη. Παρακαλώ κατεβάστε την από το https://www.python.org
    pause
    exit /b 1
)

REM Create a venv if it doesn't exist
if not exist venv\Scripts\activate (
    echo Δημιουργία virtual environment (venv)...
    python -m venv venv
)

echo Ενεργοποίηση venv...
call venv\Scripts\activate

echo Εγκατάσταση απαραίτητων βιβλιοθηκών...
pip install --upgrade pip
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo ΣΦΑΛΜΑ: Η εγκατάσταση των απαιτήσεων απέτυχε. Ελέγξτε τα σφάλματα παραπάνω.
    pause
    exit /b 1
)

echo Εκκίνηση εφαρμογής...
python main.py
IF ERRORLEVEL 1 (
    echo Κάτι πήγε στραβά. Επικοινωνήστε με τον διαχειριστή.
    pause
    exit /b 1
)

deactivate 2>nul || exit 0
pause
