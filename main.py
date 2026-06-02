import streamlit as st
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import google.generativeai as genai

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")

st.title("🔍 Greek Geocoder AI 🇬🇷")
st.write("Ιστορική Γεωγραφική Αναζήτηση (Έτος 2009 - Καποδίστριας).")

# Ανάγνωση API KEY
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.warning("⚠️ Το API Key δεν έχει ρυθμιστεί στα Secrets.")

with st.form("geocoder_global_form"):
    street = st.text_input("Περιοχή / Χωριό:", placeholder="π.χ. Σοχός, Ανώγεια, Σουφλί")
    col1, col2 = st.columns(2)
    with col1:
        number = st.text_input("Αριθμός (αν υπάρχει):", placeholder="0")
    with col2:
        postal = st.text_input("Ταχυδρομικός Κώδικας (Τ.Κ.):", placeholder="57002")
        
    submit_button = st.form_submit_button("🔍 Εύρεση Ιστορικών Στοιχείων", type="primary")

if submit_button:
    if not street:
        st.warning("⚠️ Παρακαλώ εισάγετε μια περιοχή.")
    else:
        with st.spinner("🔄 Γίνεται αναζήτηση και ιστορική ανάλυση..."):
            query = f"{street} {number}, {postal}, Greece" if postal else f"{street} {number}, Greece"
            
            try:
                geolocator = Nominatim(user_agent="greek_geocoder_v3")
                location = geolocator.geocode(query, addressdetails=True, language="el", country_codes="gr", timeout=15)

                if location:
                    addr_data = location.raw.get("address", {})
                    address_context = str(addr_data)
                    
                    # Ρύθμιση μοντέλου για μέγιστη ακρίβεια (Temperature 0)
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    generation_config = {"temperature": 0.0}
                    
                   # ΕΝΙΣΧΥΜΕΝΟ PROMPT ΜΕ ΕΣΤΙΑΣΗ ΣΤΗΝ ΟΝΟΜΑΣΙΑ
                   # ΕΝΙΣΧΥΜΕΝΟ PROMPT ΜΕ ΕΣΤΙΑΣΗ ΣΤΗΝ ΟΝΟΜΑΣΙΑ
                    prompt = (
                        f"Είσαι ο απόλυτος ειδικός στην ιστορική διοικητική διαίρεση της Ελλάδας (1997-2010).\n"
                        f"Ο χρήστης ζητά πληροφορίες για την τοποθεσία: '{street}'.\n\n"
                        f"ΟΔΗΓΙΕΣ:\n"
                        f"1. Αγνόησε οποιοδήποτε γεωγραφικό δεδομένο σου δίνει το Nominatim (OSM) αν αυτό αναφέρεται στον 'Καλλικράτη' (μετά το 2011).\n"
                        f"2. Βασίσου αποκλειστικά στις γνώσεις σου για το σχέδιο 'Καποδίστριας' (1997-2010).\n"
                        f"3. Βρες τον Δήμο Καποδίστρια στον οποίο ανήκε οικισμός '{street}' το έτος 2009. Αν ο οικισμός ήταν αυτόνομη Κοινότητα, βρες τον Δήμο στον οποίο ενσωματώθηκε.\n"
                        f"4. Βρες τον Νομό όπως ήταν το 2009.\n"
                        f"5. ΑΠΑΝΤΗΣΗ ΜΟΝΟ ΣΤΗ ΜΟΡΦΗ:\n"
                        f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα Δήμου]\n"
                        f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα Νομού]\n\n"
                        f"ΠΡΟΣΟΧΗ:\n"
                        f"- Αν ο οικισμός '{street}' δεν ανήκε σε κάποιον Δήμο Καποδίστρια, απάντησε 'ΑΓΝΩΣΤΟ'.\n"
                        f"- ΜΗΝ προσθέσεις εισαγωγικά σχόλια, επεξηγήσεις ή τη λέξη 'Κοινότητα'."
                    )
                    
                    response = model.generate_content(prompt, generation_config=generation_config)
                    ai_text = response.text.strip()
                    
                    # Parsing αποτελεσμάτων
                    pre_dimos, pre_nomos = "Δεν βρέθηκε", "Δεν βρέθηκε"
                    for line in ai_text.split('\n'):
                        if "ΠΡΟ_ΔΗΜΟΣ:" in line:
                            pre_dimos = line.replace("ΠΡΟ_ΔΗΜΟΣ:", "").strip()
                        if "ΠΡΟ_ΝΟΜΟΣ:" in line:
                            pre_nomos = line.replace("ΠΡΟ_ΝΟΜΟΣ:", "").strip()

                    # Εμφάνιση
                    st.success("✅ Ανάλυση ολοκληρώθηκε!")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("📍 Τοποθεσία")
                        st.write(location.address)
                    with c2:
                        st.success("📜 Δεδομένα 2009")
                        st.metric(label="Δήμος (Καποδίστριας)", value=pre_dimos)
                        st.metric(label="Νομός (2009)", value=pre_nomos)
                else:
                    st.error("❌ Δεν βρέθηκε η τοποθεσία στο χάρτη. Δοκιμάστε πιο συγκεκριμένα στοιχεία.")

            except Exception as e:
                st.error(f"⚠️ Σφάλμα συστήματος: {e}")