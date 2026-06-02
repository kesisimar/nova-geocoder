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
                geolocator = Nominatim(user_agent="greek_geocoder_v2")
                location = geolocator.geocode(query, addressdetails=True, language="el", country_codes="gr", timeout=15)

                if location:
                    # Λήψη όλων των διαθέσιμων δεδομένων διεύθυνσης για context
                    addr_data = location.raw.get("address", {})
                    address_context = str(addr_data)
                    
                    lat = f"{float(location.latitude):.6f}"
                    lon = f"{float(location.longitude):.6f}"
                    
                    # ΕΝΙΣΧΥΜΕΝΟ PROMPT
                    prompt = (
                        f"Είσαι κορυφαίος γεωγράφος της Ελλάδας με εξειδίκευση στη διοικητική διαίρεση 'Καποδίστριας' (1997-2010).\n"
                        f"Πληροφορίες τοποθεσίας από χάρτη: {location.address}\n"
                        f"Αναλυτικά δεδομένα: {address_context}\n\n"
                        f"Ζητούμενο:\n"
                        f"1. Βρες τον Δήμο (Καποδίστρια) στον οποίο ανήκε η περιοχή το 2009. Αν ήταν Κοινότητα, βρες τον Δήμο στον οποίο υπαγόταν.\n"
                        f"2. Βρες τον Νομό (όπως ήταν το 2009).\n"
                        f"3. Απάντησε ΑΥΣΤΗΡΑ με το format:\n"
                        f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα Δήμου]\n"
                        f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα Νομού]\n"
                        f"Μην προσθέσεις εισαγωγές, επεξηγήσεις ή τη λέξη 'Κοινότητα'."
                    )
                    
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
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
                    st.error("❌ Δεν βρέθηκε η τοποθεσία. Δοκιμάστε πιο συγκεκριμένα στοιχεία.")

            except Exception as e:
                st.error(f"⚠️ Σφάλμα συστήματος: {e}")