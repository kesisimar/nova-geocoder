# Greek Geocoder

Εφαρμογή desktop για εύρεση στοιχείων διεύθυνσης με χρήση OpenStreetMap / Nominatim.

## Εγκατάσταση

Εγκαταστήστε τις εξαρτήσεις:
# Greek Geocoder

Εφαρμογή desktop για εύρεση στοιχείων διεύθυνσης με χρήση OpenStreetMap / Nominatim.

## Απαιτήσεις
- Python 3.8+
- Σύνδεση στο διαδίκτυο (Nominatim API)

## Γρήγορη εκτέλεση

### Windows (single‑click launcher)
Δημιουργήσαμε βοηθητικά αρχεία για εύκολο, σταθερό άνοιγμα της web εφαρμογής:

- `launch_web.vbs` — διπλό κλικ ανοίγει/εκκινεί τον web server και ανοίγει το Chrome στο http://127.0.0.1:5000
- `run_web.bat` — εναλλακτικά τρέξτε αυτό αν θέλετε να δείτε logs σε παράθυρο.

Για να έχετε ένα εικονίδιο στην επιφάνεια εργασίας: κάντε δεξί κλικ στο `launch_web.vbs` → Send to → Desktop (create shortcut) ή Create shortcut και σύρετε στο Desktop.

### macOS / Linux
Τρέξτε στο terminal:

```bash
bash install_and_run.sh
```

### Χειροκίνητη εγκατάσταση

```bash
pip install -r requirements.txt
python main.py
```

## Σημειώσεις
- Απαιτεί σύνδεση στο διαδίκτυο για κλήσεις στο Nominatim.
- Παρέχεται από OpenStreetMap — σεβαστείτε τους όρους χρήσης και το rate limit.

