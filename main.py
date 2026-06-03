import streamlit as st
from geopy.geocoders import Nominatim
from pre_kallikratis import map_pre_kallikratis

# Ρυθμίσεις σελίδας
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder 🇬🇷")

# Input form
with st.form("geocoder_form"):
    street = st.text_input("Οδός / Περιοχή / Χωριό:")
    number = st.text_input("Αριθμός:")
    postal = st.text_input("Τ.Κ.:")
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ εισάγετε τοποθεσία.")
    else:
        with st.spinner("🔄 Αναζήτηση στη βάση δεδομένων..."):
            try:
                geolocator = Nominatim(user_agent="my_unique_geocoder_app_2026")
                location = geolocator.geocode(f"{street} {number}, {postal}, Greece", addressdetails=True, timeout=10)

                if not location:
                    st.error("❌ Δεν βρέθηκε η τοποθεσία στον χάρτη.")
                else:
                    addr = location.raw.get("address", {})
                    dimos = addr.get("municipality") or addr.get("city") or "—"
                    
                    # ΕΛΕΓΧΟΣ ΜΟΝΟ ΣΤΟ CSV - ΤΟ ΑΙ ΔΕΝ ΚΑΛΕΙΤΑΙ ΠΟΤΕ
                    pre_dimos, pre_nomos = map_pre_kallikratis(addr)
                    
                    if not pre_dimos or pre_dimos == "—":
                        st.warning("⚠️ Το χωριό δεν βρέθηκε στη βάση δεδομένων. Προσθέστε το στο CSV.")
                    else:
                        st.success("✅ Βρέθηκαν στοιχεία!")
                        c1, c2 = st.columns(2)
                        c1.metric("Σημερινός Δήμος", dimos)
                        c2.metric("Ιστορικός Δήμος (2009)", pre_dimos)
                        st.info(f"📍 {location.address}")

            except Exception as e:
                st.error(f"⚠️ Σφάλμα: {e}")