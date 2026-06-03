import streamlit as st
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import google.generativeai as genai
from pre_kallikratis import map_pre_kallikratis
import time

# Page setup
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder AI 🇬🇷")

# Αρχικοποίηση AI (Με cache για να μην πληρώνουμε API κλήσεις)
@st.cache_data(ttl=3600)
def get_ai_response(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# Load API key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Input form
with st.form("geocoder_global_form"):
    street = st.text_input("Οδός / Περιοχή / Χωριό:")
    col1, col2 = st.columns(2)
    number = col1.text_input("Αριθμός:")
    postal = col2.text_input("Τ.Κ.:")
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ εισάγετε μια τοποθεσία.")
    else:
        with st.spinner("🔄 Αναζήτηση..."):
            try:
                geolocator = Nominatim(user_agent="greek_geocoder_final_prod")
                location = geolocator.geocode(f"{street} {number}, {postal}, Greece", addressdetails=True, language="el", country_codes="gr", timeout=10)

                if not location:
                    st.error("❌ Η διεύθυνση δεν βρέθηκε.")
                else:
                    addr = location.raw.get("address", {})
                    nomos = addr.get("county") or addr.get("state") or "—"
                    dimos = addr.get("municipality") or addr.get("city") or "—"

                    # 1. Έλεγχος στο CSV (Ακαριαίο, Δωρεάν)
                    pre_dimos, pre_nomos = map_pre_kallikratis(addr)
                    
                    # 2. ΜΟΝΟ αν δεν υπάρχει στο CSV, ρωτάμε το AI
                    if (not pre_dimos or pre_dimos == "—") and "GEMINI_API_KEY" in st.secrets:
                        prompt = (
                            f"Βρες τον Δήμο (1997-2010) και τον Νομό (1997-2010) για: {location.address}. "
                            f"Απάντησε μόνο σε 2 γραμμές:\n"
                            f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα]\n"
                            f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα]"
                        )
                        try:
                            ai_text = get_ai_response(prompt)
                            for line in ai_text.split('\n'):
                                if "ΠΡΟ_ΔΗΜΟΣ:" in line: pre_dimos = line.split(":")[1].strip()
                                if "ΠΡΟ_ΝΟΜΟΣ:" in line: pre_nomos = line.split(":")[1].strip()
                        except:
                            st.error("⚠️ Το AI δεν μπόρεσε να απαντήσει (API Limit).")

                    # Display
                    st.success("✅ Τα στοιχεία εντοπίστηκαν!")
                    c1, c2 = st.columns(2)
                    c1.metric("Σημερινός Δήμος", dimos)
                    c2.metric("Ιστορικός Δήμος (2009)", pre_dimos or "—")
                    st.info(f"📍 {location.address}")

            except Exception as e:
                st.error(f"⚠️ Σφάλμα: {e}")