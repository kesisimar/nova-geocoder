import streamlit as st
import pandas as pd
import os

# Ρυθμίσεις σελίδας
st.set_page_config(page_title="Greek Geocoder", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder 🇬🇷")
st.write("Επιλέξτε μια περιοχή για εύρεση ιστορικών στοιχείων.")

# 1. Φόρτωση δεδομένων (Caching για ταχύτητα)
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), 'data', 'dimoi.csv')
    return pd.read_csv(path)

# Input form
df = load_data()
with st.form("geocoder_form"):
    # Χρησιμοποιούμε τη στήλη 'name' από το CSV
    all_names = sorted(df['name'].unique().tolist())
    street = st.selectbox("Επιλέξτε Δήμο / Περιοχή:", [""] + all_names)
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ επιλέξτε μια περιοχή από τη λίστα.")
    else:
        # Φιλτράρισμα του DataFrame με βάση το όνομα
        result = df[df['name'] == street]
        
        if result.empty:
            st.error("❌ Δεν βρέθηκαν στοιχεία για αυτή την περιοχή.")
        else:
            # Παίρνουμε την πρώτη εγγραφή
            row = result.iloc[0]
            
            st.success("✅ Βρέθηκαν ιστορικά στοιχεία!")
            
            # Εμφάνιση αποτελεσμάτων
            c1, c2 = st.columns(2)
            c1.metric("Ιστορικό Όνομα", row['name'])
            c1.metric("Τύπος", row['typos'])
            
            c2.metric("Νομός (2009)", row['nomos'])
            c2.metric("Περιφέρεια", row['perifereia'])
            
            st.write(f"**Έδρα:** {row['edra']}")
            st.write(f"**Κωδικός:** {row['kodikos']}")

# Σημείωση: Το Geopy δεν χρειάζεται πια αν βασιζόμαστε στο CSV σου.