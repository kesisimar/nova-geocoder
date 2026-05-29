import streamlit as st
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import google.generativeai as genai

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")

st.title("🔍 Greek Geocoder AI 🇬🇷")
st.write("Ιστορική Γεωγραφική Αναζήτηση και ΤΚ για την εργασία σου.")

# Ασφαλής ανάγνωση του API KEY από τα Secrets του Streamlit
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Σφάλμα ρύθμισης AI: {e}")
else:
    st.warning("⚠️ Το API Key δεν έχει ρυθμιστεί στα Secrets του Streamlit.")
    GEMINI_API_KEY = None

# Φόρμα Εισαγωγής
with st.form("geocoder_global_form"):
    street = st.text_input("Οδός / Περιοχή / Χωριό:", placeholder="π.χ. Σοχός, Ζαγκλιβέρι")
    col1, col2 = st.columns(2)
    with col1:
        number = st.text_input("Αριθμός:", placeholder="0")
    with col2:
        postal = st.text_input("Ταχυδρομικός Κώδικας (Τ.Κ.):", placeholder="57002")
    submit_button = st.form_submit_button("🔍 Εύρεση Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ εισάγετε μια τοποθεσία.")
    elif not GEMINI_API_KEY:
        st.error("❌ Δεν βρέθηκε API Key.")
    else:
        with st.spinner("🔄 Γίνεται ανάλυση..."):
            query = f"{street} {number}, {postal}, Greece" if postal else f"{street} {number}, Greece"
            try:
                geolocator = Nominatim(user_agent="greek_geocoder_final_prod")
                location = geolocator.geocode(query, addressdetails=True, language="el", country_codes="gr", timeout=10)

                if location:
                    addr = location.raw.get("address", {})
                    nomos = addr.get("county") or addr.get("state_district") or addr.get("state") or "—"
                    dimos = addr.get("municipality") or addr.get("city") or addr.get("town") or "—"
                    
                    # --- ΠΡΟΧΩΡΗΜΕΝΟ PROMPT ΜΕ ΤΚ ---
                    pre_dimos, pre_nomos = "—", "—"
                    current_tk, old_tk = "—", "—"
                    
                    prompt = (
                        f"Είσαι γεωγράφος. Τοποθεσία '{location.address}'.\n"
                        f"1) Ποιος είναι ο επίσημος Τρέχων ΤΚ;\n"
                        f"2) Υπήρχε άλλος (παλαιότερος) ΤΚ στην περιοχή;\n"
                        f"3) Δήμος (Καποδίστριας) το 2009.\n"
                        f"4) Νομός το 2009.\n"
                        f"Απάντησε αυστηρά χωρίς άλλα λόγια:\n"
                        f"ΤΡΕΧΩΝ_ΤΚ: [ΤΚ]\n"
                        f"ΠΑΛΙΟΣ_ΤΚ: [ΤΚ ή 'Δεν υπάρχει']\n"
                        f"ΠΡΟ_ΔΗΜΟΣ: [Δήμος 2009]\n"
                        f"ΠΡΟ_ΝΟΜΟΣ: [Νομός 2009]"
                    )
                    
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        response = model.generate_content(prompt)
                        ai_text = response.text.strip()
                        
                        for line in ai_text.split('\n'):
                            if "ΤΡΕΧΩΝ_ΤΚ:" in line: current_tk = line.replace("ΤΡΕΧΩΝ_ΤΚ:", "").strip()
                            if "ΠΑΛΙΟΣ_ΤΚ:" in line: old_tk = line.replace("ΠΑΛΙΟΣ_ΤΚ:", "").strip()
                            if "ΠΡΟ_ΔΗΜΟΣ:" in line: pre_dimos = line.replace("ΠΡΟ_ΔΗΜΟΣ:", "").strip()
                            if "ΠΡΟ_ΝΟΜΟΣ:" in line: pre_nomos = line.replace("ΠΡΟ_ΝΟΜΟΣ:", "").strip()
                    except Exception:
                        pass

                    # --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ---
                    st.success("✅ Τα στοιχεία εντοπίστηκαν!")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("🏛️ Σημερινή Μορφή")
                        st.metric(label="Τρέχων ΤΚ", value=current_tk)
                        st.metric(label="Δήμος (Καλλικράτης)", value=dimos)
                    with c2:
                        st.success("📜 Ιστορική Μορφή (2009)")
                        st.metric(label="Παλιός ΤΚ", value=old_tk)
                        st.metric(label="Δήμος (Καποδίστριας)", value=pre_dimos)
                    
                    st.info(f"🗺️ **Πλήρης Διεύθυνση:**\n{location.address}")
                else:
                    st.error("❌ Δεν βρέθηκε η τοποθεσία.")
            except Exception as e:
                st.error(f"⚠️ Σφάλμα: {e}")