import streamlit as st
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import google.generativeai as genai


# Page setup
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")
st.title("🔍 Greek Geocoder AI 🇬🇷")
st.write("Ιστορική Γεωγραφική Αναζήτηση για όλα τα χωριά και τις πόλεις της Ελλάδας.")


# Load API key from Streamlit secrets (if present)
GEMINI_API_KEY = None
if "GEMINI_API_KEY" in st.secrets:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Σφάλμα ρύθμισης AI: {e}")
else:
    st.warning("⚠️ Το API Key δεν έχει ρυθμιστεί ακόμα στα Secrets του Streamlit.")
    GEMINI_API_KEY = None


# Input form
with st.form("geocoder_global_form"):
    street = st.text_input("Οδός / Περιοχή / Χωριό:", placeholder="π.χ. Σοχός, Ζαγκλιβέρι, Ανώγεια, Σουφλί")
    col1, col2 = st.columns(2)
    with col1:
        number = st.text_input("Αριθμός (αν υπάρχει):", placeholder="e.g. 0")
    with col2:
        postal = st.text_input("Ταχυδρομικός Κώδικας (Τ.Κ.):", placeholder="e.g. 57002")

    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")


if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ εισάγετε μια οδό, περιοχή ή χωριό.")
    elif not GEMINI_API_KEY:
        st.error("❌ Δεν βρέθηκε ενεργό API Key στα Secrets του Streamlit. Παρακαλώ προσθέστε το.")
    else:
        with st.spinner("🔄 Γίνεται αυτόματη αναζήτηση και ανάλυση Δήμων..."):
            query = f"{street} {number}, {postal}, Greece" if postal else f"{street} {number}, Greece"

            try:
                geolocator = Nominatim(user_agent="greek_geocoder_final_prod")
                location = geolocator.geocode(query, addressdetails=True, language="el", country_codes="gr", timeout=10)

                if not location:
                    st.error("❌ Η διεύθυνση δεν βρέθηκε στο χάρτη. Δοκιμάστε ξανά.")
                else:
                    addr = location.raw.get("address", {})
                    nomos = addr.get("county") or addr.get("state_district") or addr.get("state") or "—"
                    dimos = addr.get("municipality") or addr.get("city") or addr.get("town") or "—"

                    lat = f"{float(location.latitude):.6f}"
                    lon = f"{float(location.longitude):.6f}"

                    # Deterministic placeholders (will use CSV mapping / fallback LLM)
                    pre_dimos = "—"
                    pre_nomos = "—"

                    # Strict Greek prompt for LLM fallback (only used when needed)
                    prompt = (
                        f"Είσαι κορυφαίος γεωγράφος της Ελλάδας. Με βάση τη σημερινή τοποθεσία '{location.address}', "
                        f"τον τρέχοντα Δήμο '{dimos}' και τον Νομό '{nomos}', βρες τα εξής στοιχεία:\n"
                        f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα Δήμου το 2009]\n"
                        f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα Νομού το 2009]"
                    )

                    # Call LLM only as fallback
                    import time
                    try:
                        # Find available model dynamically
                        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        
                        # Try models in order of preference
                        model_candidates = ['models/gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-2.0-flash']
                        chosen_model = None
                        for candidate in model_candidates:
                            if candidate in available_models:
                                chosen_model = candidate
                                break
                        
                        if not chosen_model:
                            # Fallback: use first available model
                            if available_models:
                                chosen_model = available_models[0]
                            else:
                                raise Exception("No models with generateContent support found")
                        
                        model = genai.GenerativeModel(chosen_model)
                        
                        # Retry logic for rate limiting (429 errors)
                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                response = model.generate_content(prompt)
                                ai_text = (response.text or "").strip()
                                for line in ai_text.split('\n'):
                                    if line.startswith("ΠΡΟ_ΔΗΜΟΣ:"):
                                        pre_dimos = line.replace("ΠΡΟ_ΔΗΜΟΣ:", "").strip()
                                    if line.startswith("ΠΡΟ_ΝΟΜΟΣ:"):
                                        pre_nomos = line.replace("ΠΡΟ_ΝΟΜΟΣ:", "").strip()
                                break  # Success, exit retry loop
                            except Exception as retry_err:
                                if "429" in str(retry_err) and attempt < max_retries - 1:
                                    wait_time = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                                    st.info(f"Rate limit hit. Retrying in {wait_time}s...")
                                    time.sleep(wait_time)
                                else:
                                    raise
                    except Exception as ai_err:
                        # keep deterministic placeholders if LLM fails
                        st.warning(f"AI fallback failed: {ai_err}")

                    # Display results
                    st.success("✅ Τα στοιχεία εντοπίστηκαν!")
                    st.markdown(f"### 📍 Αναζήτηση: *{street} {number}*")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("🏛️ Σημερινή Διοικητική Μορφή")
                        st.metric(label="Δήμος (Καλλικράτης)", value=dimos)
                        st.metric(label="Νομός / Περιφέρεια", value=nomos)
                        st.metric(label="🌍 Γεωγραφικό Πλάτος (Lat)", value=f"{lat}°")

                    with c2:
                        st.success("📜 Ιστορική Μορφή (Έτος 2009)")
                        st.metric(label="Δήμος (Καποδίστριας 2009)", value=pre_dimos)
                        st.metric(label="Ιστορικός Νομός (2009)", value=pre_nomos)
                        st.metric(label="🧭 Γεωγραφικό Μήκος (Lon)", value=f"{lon}°")

                    st.info(f"🗺️ **Πλήρης Διεύθυνση (OSM):**\n{location.address}")

            except geopy_exc.GeocoderTimedOut:
                st.error("⚠️ Η αναζήτηση χρονομετρήθηκε. Δοκιμάστε ξανά.")
            except Exception as e:
                st.error(f"⚠️ Σφάλμα: {e}")
