import csv
import os
import unicodedata

_mapping = {}

def strips_accents_and_upper(text):
    if not text:
        return ""
    text = str(text).strip().lower()
    text = text.replace("δήμος", "").replace("δημος", "").replace("κοινότητα", "").replace("κοινοτητα", "").strip()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.upper()

def _load():
    global _mapping
    if _mapping:
        return
    path = os.path.join(os.path.dirname(__file__), 'data', 'pre_kallikratis.csv')
    if not os.path.exists(path):
        return
    with open(path, newline='', encoding='utf-8') as f:
        # Διαβάζουμε το CSV με απλό reader για να πιάσουμε τις στήλες με τη σειρά (0, 1, 2)
        # χωρίς να μας νοιάζει πώς ονομάζονται οι τίτλοι τους!
        reader = csv.reader(f)
        header = next(reader, None) # Προσπερνάμε την πρώτη γραμμή με τους τίτλους
        
        for row in reader:
            if len(row) >= 3:
                # Υποθέτουμε: στήλη 0 = Τρέχον Όνομα, στήλη 1 = Παλιός Νομός, στήλη 2 = Παλιός Δήμος
                key = strips_accents_and_upper(row[0])
                if key:
                    _mapping[key] = (row[1].strip(), row[2].strip())

def map_pre_kallikratis(addr: dict):
    _load()
    if not addr:
        return (None, None)
        
    # Ενώνουμε όλα τα στοιχεία της διεύθυνσης σε ένα μεγάλο κείμενο
    full_text_components = [str(val) for val in addr.values() if val]
    full_address_clean = strips_accents_and_upper(" ".join(full_text_components))
    
    # Ψάχνουμε αν κάποιο κλειδί από το CSV υπάρχει μέσα στη διεύθυνση
    for current_name, result in _mapping.items():
        if current_name in full_address_clean and len(current_name) > 3:
            return result
            
    return (None, None)