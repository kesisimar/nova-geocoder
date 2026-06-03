import streamlit as st
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import google.generativeai as genai

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")

st.title("🔍 Greek Geocoder AI 🇬🇷")

# Ασφαλής ανάγνωση του API KEY
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Το API Key δεν έχει ρυθμιστεί στα Secrets.")
    st.stop()

with st.form("geocoder_form"):
    street = st.text_input("Τοποθεσία:")
    postal = st.text_input("Τ.Κ.:")
    submit_button = st.form_submit_button("🔍 Αναζήτηση")

if submit_button and street:
    with st.spinner("🔄 Γίνεται αναζήτηση..."):
        try:
            geolocator = Nominatim(user_agent="my_geocoder_app_123")
            query = f"{street}, {postal}, Greece" if postal else f"{street}, Greece"
            location = geolocator.geocode(query, addressdetails=True, language="el", timeout=10)

            if location:
                addr = location.raw.get("address", {})
                nomos = addr.get("county") or addr.get("state") or "—"
                dimos = addr.get("municipality") or addr.get("city") or "—"
                
                # --- ΣΩΣΤΗ ΔΗΜΙΟΥΡΓΙΑ PROMPT ---
                # Ορίζουμε το prompt ΠΑΝΤΑ πριν την κλήση
                prompt = (
                    f"Είσαι γεωγράφος. Τοποθεσία: '{location.address}'. "
                    f"Βρες: 1) Τρέχων ΤΚ, 2) Παλαιότερο ΤΚ, 3) Δήμο 2009, 4) Νομό 2009. "
                    f"Απάντησε αυστηρά σε αυτή τη μορφή:\n"
                    f"ΤΡΕΧΩΝ_ΤΚ: [ΤΚ]\nΠΑΛΙΟΣ_ΤΚ: [ΤΚ]\nΠΡΟ_ΔΗΜΟΣ: [Δήμος 2009]\nΠΡΟ_ΝΟΜΟΣ: [Νομός 2009]"
                )
                
                # Χρήση έγκυρου μοντέλου από τη λίστα σου
                model = genai.GenerativeModel('gemini-2.0-flash') 
                response = model.generate_content(prompt)
                ai_text = response.text.strip()
                
                # Default τιμές
                res = {"ΤΡΕΧΩΝ_ΤΚ": "—", "ΠΑΛΙΟΣ_ΤΚ": "—", "ΠΡΟ_ΔΗΜΟΣ": "—", "ΠΡΟ_ΝΟΜΟΣ": "—"}
                
                for line in ai_text.split('\n'):
                    for key in res.keys():
                        if key in line:
                            res[key] = line.split(":", 1)[1].strip()

                # Εμφάνιση
                st.success("✅ Βρέθηκαν στοιχεία!")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Τρέχων ΤΚ", res["ΤΡΕΧΩΝ_ΤΚ"])
                    st.metric("Δήμος (Καλλικράτης)", dimos)
                with c2:
                    st.metric("Παλιός ΤΚ", res["ΠΑΛΙΟΣ_ΤΚ"])
                    st.metric("Δήμος 2009", res["ΠΡΟ_ΔΗΜΟΣ"])
                    
            else:
                st.error("❌ Δεν βρέθηκε η τοποθεσία.")
        except Exception as e:
            st.error(f"⚠️ Σφάλμα: {e}")