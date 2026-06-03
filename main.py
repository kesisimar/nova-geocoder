import streamlit as st

from geopy.geocoders import Nominatim

import geopy.exc as geopy_exc

import google.generativeai as genai



# Ρύθμιση Σελίδας στον Browser

st.set_page_config(page_title="Greek Geocoder AI", page_icon="📍", layout="centered")



st.title("🔍 Greek Geocoder AI 🇬🇷")

st.write("Ιστορική Γεωγραφική Αναζήτηση για όλα τα χωριά και τις πόλεις της Ελλάδας.")



# Ασφαλής ανάγνωση του API KEY αποκλειστικά από τα Secrets του Streamlit

if "GEMINI_API_KEY" in st.secrets:

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

try:

genai.configure(api_key=GEMINI_API_KEY)

except Exception as e:

st.error(f"Σφάλμα ρύθμισης AI: {e}")

else:

st.warning("⚠️ Το API Key δεν έχει ρυθμιστεί ακόμα στα Secrets του Streamlit.")

GEMINI_API_KEY = None



# Φόρμα Εισαγωγής Στοιχείων

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



if location:

addr = location.raw.get("address", {})

nomos = addr.get("county") or addr.get("state_district") or addr.get("state") or "—"

dimos = addr.get("municipality") or addr.get("city") or addr.get("town") or "—"


lat = f"{float(location.latitude):.6f}"

lon = f"{float(location.longitude):.6f}"


# --- ΠΡΟΧΩΡΗΜΕΝΟ PROMPT (ΕΤΟΣ 2009 - ΜΟΝΟ ΔΗΜΟΙ) ---

pre_dimos = "—"

pre_nomos = "—"


prompt = (

f"Είσαι κορυφαίος γεωγράφος της Ελλάδας. Με βάση τη σημερινή τοποθεσία '{location.address}', "

f"τον τρέχοντα Δήμο '{dimos}' και τον Νομό '{nomos}', βρες τα εξής στοιχεία:\n"

f"1) Ποιος ήταν ο Δήμος (ΑΠΟΚΛΕΙΣΤΙΚΑ ΔΗΜΟΣ, ΟΧΙ ΚΟΙΝΟΤΗΤΑ) στον οποίο ανήκε η τοποθεσία το έτος 2009 (προ-Καλλικράτη επί Καποδίστρια).\n"

f"2) Ποιος ήταν ο Νομός το έτος 2009.\n"

f"Αν το 2009 η περιοχή ήταν αυτόνομη Κοινότητα, βρες σε ποιον Δήμο Καποδίστρια υπαγόταν ή ανάφερέ τον ως Δήμο. Μην γράψεις τη λέξη 'Κοινότητα'.\n"

f"Απάντησε αυστηρά και πολύ σύντομα σε αυτή τη μορφή χωρίς άλλα λόγια:\n"

f"ΠΡΟ_ΔΗΜΟΣ: [Όνομα Δήμου το 2009]\n"

f"ΠΡΟ_ΝΟΜΟΣ: [Όνομα Νομού το 2009]"

)


try:

model = genai.GenerativeModel('gemini-2.5-flash')

response = model.generate_content(prompt)

ai_text = response.text.strip()


for line in ai_text.split('\n'):

if "ΠΡΟ_ΔΗΜΟΣ:" in line:

pre_dimos = line.replace("ΠΡΟ_ΔΗΜΟΣ:", "").strip()

if "ΠΡΟ_ΝΟΜΟΣ:" in line:

pre_nomos = line.replace("ΠΡΟ_ΝΟΜΟΣ:", "").strip()

except Exception as ai_err:

pre_dimos = "Σφάλμα AI"

pre_nomos = f"{ai_err}"



# --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ΣΤΗΝ ΟΘΟΝΗ ---

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

else:

st.error("❌ Η διεύθυνση δεν βρέθηκε στο χάρτη. Δοκιμάστε ξανά.")



except geopy_exc.GeocoderTimedOut:

st.error("⚠️ Η αναζήτηση χρονομετρήθηκε. Δοκιμάστε ξανά.")

except Exception as e:

st.error(f"⚠️ Σφάλμα: {e}")