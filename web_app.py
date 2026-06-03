from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import geopy.exc as geopy_exc
import socket
from pre_kallikratis import map_pre_kallikratis

app = Flask(__name__)


def check_internet() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except Exception:
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        street = request.form.get('street', '').strip()
        number = request.form.get('number', '').strip()
        postal = request.form.get('postal', '').strip()

        if not street or not number:
            error = 'Συμπληρώστε τουλάχιστον την οδό και τον αριθμό.'
        elif not check_internet():
            error = 'Δεν υπάρχει σύνδεση στο διαδίκτυο.'
        else:
            query = f"{street} {number}, {postal}, Greece" if postal else f"{street} {number}, Greece"
            try:
                geolocator = Nominatim(user_agent="greek_geocoder_web_v1")
                location = geolocator.geocode(query, addressdetails=True, language='el', country_codes='gr', timeout=10)
                if location:
                    addr = location.raw.get('address', {})
                    nomos = addr.get('county') or addr.get('state_district') or addr.get('state') or '—'
                    dimos = addr.get('municipality') or addr.get('city') or addr.get('town') or addr.get('village') or addr.get('suburb') or '—'
                    pre_nomos, pre_dimos = map_pre_kallikratis(addr)
                    lat = f"{float(location.latitude):.6f}"
                    lon = f"{float(location.longitude):.6f}"
                    result = {
                        'queried': f"{street} {number}, ΤΚ {postal}",
                        'nomos': nomos,
                        'addr_raw': addr,
                        'pre_nomos': pre_nomos,
                        'dimos': dimos,
                        'pre_dimos': pre_dimos,
                        'lat': lat,
                        'lon': lon,
                        'address': location.address,
                    }
                else:
                    error = 'Η διεύθυνση δεν βρέθηκε. Δοκιμάστε με διαφορετικά στοιχεία.'
            except geopy_exc.GeocoderTimedOut:
                error = 'Η αναζήτηση χρονομετρήθηκε. Δοκιμάστε ξανά αργότερα.'
            except geopy_exc.GeocoderServiceError as e:
                error = f'Σφάλμα υπηρεσίας γεωκωδικοποίησης: {e}'
            except Exception as e:
                error = f'Σφάλμα: {e}'

    return render_template('index.html', result=result, error=error)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
