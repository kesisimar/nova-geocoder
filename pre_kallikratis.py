import csv, os, unicodedata

_mapping = {}

def strips(text):
    text = str(text).strip().lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.upper()

def _load():
    global _mapping
    if _mapping: return
    # Βεβαιώσου ότι το αρχείο είναι στο φάκελο data/
    path = os.path.join(os.path.dirname(__file__), 'data', 'pre_kallikratis.csv')
    if not os.path.exists(path): return
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) # Παράκαμψη κεφαλίδας
        for row in reader:
            if len(row) >= 3:
                _mapping[strips(row[0])] = (row[1].strip(), row[2].strip())

def map_pre_kallikratis(addr: dict):
    _load()
    full_addr = strips(" ".join([str(val) for val in addr.values()]))
    
    sorted_keys = sorted(_mapping.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in full_addr:
            nomos, dimos = _mapping[key]
            return (dimos, nomos)
    return ("—", "—")