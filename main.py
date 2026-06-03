import streamlit as st
import google.generativeai as genai
from geopy.geocoders import Nominatim
from pre_kallikratis import map_pre_kallikratis

# Ρυθμίσεις σελίδας
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder AI 🇬🇷")

# Αρχικοποίηση AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Ρύθμισε το GEMINI_API_KEY στα Streamlit Secrets!")
    st.stop()

# Οικονομική συνάρτηση για AI (με Cache)
@st.cache_data(ttl=3600)
def get_ai_historical_data(prompt):
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config={"temperature": 0.0})
    response = model.generate_content(prompt)
    return response.text

with st.form("geocoder_form"):
    street = st.text_input("Οδός / Περιοχή / Χωριό:")
    col1, col2 = st.columns(2)
    number = col1.text_input("Αριθμός:")
    postal = col2.text_input("Τ.Κ.:")
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button and street:
    with st.spinner("🔄 Αναζήτηση..."):
        query = f"{street} {number}, {postal}, Greece"
        geolocator = Nominatim(user_agent="greek_geocoder_prod")
        location = geolocator.geocode(query, addressdetails=True, language="el", country_codes="gr", timeout=10)

        if not location:
            st.error("❌ Δεν βρέθηκε η τοποθεσία.")
        else:
            addr = location.raw.get("address", {})
            nomos = addr.get("county") or addr.get("state") or "—"
            dimos = addr.get("municipality") or addr.get("city") or "—"

            # 1. Πρώτα έλεγχος στο CSV (Δωρεάν)
            pre_dimos, pre_nomos = map_pre_kallikratis(addr)
            
            # 2. Αν δεν υπάρχει στο CSV, ρωτάμε το AI
            if not pre_dimos or pre_dimos == "—":
                prompt = (
                    f"Είσαι ειδικός γεωγράφος της Ελλάδας. Βρες τον Δήμο (Καποδίστριας 2009) και τον Νομό (2009) για: {location.address}.\n"
                    f"ΠΡΟΣΟΧΗ: Μην επιστρέψεις Περιφέρειες. Απάντησε ΑΥΣΤΗΡΑ με το φορμάτ:\n"
                    f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα Δήμου 2009]\n"
                    f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα Νομού 2009]"
                )
                ai_text = get_ai_historical_data(prompt)
                for line in ai_text.split('\n'):
                    if line.startswith("ΠΡΟ_ΔΗΜΟΣ:"): pre_dimos = line.replace("ΠΡΟ_ΔΗΜΟΣ:", "").strip()
                    if line.startswith("ΠΡΟ_ΝΟΜΟΣ:"): pre_nomos = line.replace("ΠΡΟ_ΝΟΜΟΣ:", "").strip()

            st.success("✅ Στοιχεία:")
            c1, c2 = st.columns(2)
            c1.metric("Σημερινός Δήμος", dimos)
            c2.metric("Ιστορικός Δήμος (2009)", pre_dimos or "—")
            st.info(f"📍 {location.address}")