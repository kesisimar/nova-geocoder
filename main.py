import streamlit as st
from geopy.geocoders import Nominatim
from pre_kallikratis import map_pre_kallikratis
import csv
import os

# Ρυθμίσεις σελίδας
st.set_page_config(page_title="Greek Geocoder", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder 🇬🇷")
st.write("Επιλέξτε μια περιοχή από τη βάση δεδομένων για εύρεση ιστορικών στοιχείων (1997-2010).")

# Συνάρτηση για ανάκτηση ονομάτων από το CSV
@st.cache_data
def get_all_village_names():
    names = []
    path = os.path.join(os.path.dirname(__file__), 'data', 'pre_kallikratis.csv')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Παράκαμψη κεφαλίδας
            for row in reader:
                if row: names.append(row[0].strip())
    return sorted(list(set(names)))

# Input form
with st.form("geocoder_form"):
    # Δυναμική λίστα επιλογών
    all_names = get_all_village_names()
    street = st.selectbox("Επιλέξτε χωριό / περιοχή:", [""] + all_names)
    
    number = st.text_input("Αριθμός (προαιρετικά):")
    postal = st.text_input("Τ.Κ. (προαιρετικά):")
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ επιλέξτε μια περιοχή από τη λίστα.")
    else:
        with st.spinner("🔄 Αναζήτηση στη βάση δεδομένων..."):
            try:
                # Nominatim API για γεωγραφικό εντοπισμό
                geolocator = Nominatim(user_agent="greek_geocoder_v2026")
                query = f"{street}, Greece" 
                location = geolocator.geocode(query, addressdetails=True, timeout=10)

                if not location:
                    st.error("❌ Δεν βρέθηκε η τοποθεσία στον χάρτη.")
                else:
                    addr = location.raw.get("address", {})
                    dimos_current = addr.get("municipality") or addr.get("city") or "—"
                    
                    # Αναζήτηση στο CSV
                    pre_dimos, pre_nomos = map_pre_kallikratis(addr)
                    
                    # Αν δεν βρέθηκε με την αυτόματη μέθοδο, δοκιμάζουμε απευθείας με το όνομα της επιλογής
                    if pre_dimos == "—":
                        # Dummy addr για να αναγκάσουμε το CSV να ψάξει με το όνομα που επιλέξαμε
                        pre_dimos, pre_nomos = map_pre_kallikratis({'search': street})

                    if pre_dimos == "—":
                        st.warning("⚠️ Δεν βρέθηκαν ιστορικά στοιχεία για αυτή την περιοχή στο CSV.")
                    else:
                        st.success("✅ Βρέθηκαν ιστορικά στοιχεία!")
                        c1, c2 = st.columns(2)
                        c1.metric("Σημερινός Δήμος", dimos_current)
                        c2.metric("Ιστορικός Δήμος (2009)", pre_dimos)
                        c2.metric("Ιστορικός Νομός (2009)", pre_nomos)
                        st.info(f"📍 Τοποθεσία (OSM): {location.address}")

            except Exception as e:
                st.error(f"⚠️ Σφάλμα σύνδεσης: {e}")