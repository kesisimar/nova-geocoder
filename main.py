import streamlit as st
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import google.generativeai as genai
from pre_kallikratis import map_pre_kallikratis
import time

# Page setup
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder AI 🇬🇷")

# --- ΟΙΚΟΝΟΜΙΚΗ ΣΥΝΑΡΤΗΣΗ ΜΕ CACHE ---
@st.cache_data(ttl=3600)
def get_ai_historical_data(prompt):
    # Χρησιμοποιούμε το lite μοντέλο και μηδενική θερμοκρασία για ακρίβεια
    model = genai.GenerativeModel('gemini-2.0-flash-lite', generation_config={"temperature": 0.0})
    response = model.generate_content(prompt)
    return response.text

# Load API key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Ρύθμισε το API KEY στα Secrets!")
    st.stop()

# Input form
with st.form("geocoder_global_form"):
    street = st.text_input("Οδός / Περιοχή / Χωριό:")
    col1, col2 = st.columns(2)
    with col1:
        number = st.text_input("Αριθμός:")
    with col2:
        postal = st.text_input("Τ.Κ.:")
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ εισάγετε περιοχή.")
    else:
        with st.spinner("🔄 Αναζήτηση..."):
            query = f"{street} {number}, {postal}, Greece"
            try:
                geolocator = Nominatim(user_agent="greek_geocoder_prod")
                location = geolocator.geocode(query, addressdetails=True, language="el", country_codes="gr", timeout=10)

                if not location:
                    st.error("❌ Δεν βρέθηκε η τοποθεσία.")
                else:
                    addr = location.raw.get("address", {})
                    nomos = addr.get("county") or addr.get("state") or "—"
                    dimos = addr.get("municipality") or addr.get("city") or "—"

                    # 1. Deterministic lookup
                    pre_dimos, pre_nomos = map_pre_kallikratis(addr)
                    
                    # 2. LLM Fallback (Μόνο αν δεν βρεθεί στο CSV)
                    if pre_dimos is None or pre_dimos == "—":
                        prompt = prompt = (
                    f"Είσαι ειδικός γεωγράφος της Ελλάδας. Βρες τον Δήμο (Καποδίστριας 2009) για την τοποθεσία: {location.address}.\n"
                    f"Σημερινός Δήμος: {dimos}, Νομός: {nomos}.\n\n"
                    f"ΠΑΡΑΔΕΙΓΜΑΤΑ ΑΠΑΝΤΗΣΗΣ:\n"
                    f"Αν η περιοχή είναι ο Σοχός, η απάντηση είναι:\n"
                    f"ΠΡΟ_ΔΗΜΟΣ: Δήμος Σοχού\n"
                    f"ΠΡΟ_ΝΟΜΟΣ: Νομός Θεσσαλονίκης\n\n"
                    f"Τώρα απάντησε για την περιοχή που σου έδωσα, ακολουθώντας ΑΚΡΙΒΩΣ αυτό το φορμάτ:\n"
                    f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα Δήμου 2009]\n"
                    f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα Νομού 2009]\n"
                    f"Αν δεν είσαι σίγουρος, γράψε 'Δεν βρέθηκε'."
                )
                        ai_text = get_ai_historical_data(prompt)
                        for line in ai_text.split('\n'):
                            if line.startswith("ΠΡΟ_ΔΗΜΟΣ:"): pre_dimos = line.replace("ΠΡΟ_ΔΗΜΟΣ:", "").strip()
                            if line.startswith("ΠΡΟ_ΝΟΜΟΣ:"): pre_nomos = line.replace("ΠΡΟ_ΝΟΜΟΣ:", "").strip()

                    # Display
                    st.success("✅ Βρέθηκαν στοιχεία!")
                    col1, col2 = st.columns(2)
                    col1.metric("Σημερινός Δήμος", dimos)
                    col2.metric("Ιστορικός Δήμος (2009)", pre_dimos or "—")
                    st.info(f"📍 {location.address}")

            except Exception as e:
                st.error(f"⚠️ Σφάλμα: {e}")