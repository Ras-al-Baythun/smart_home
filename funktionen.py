from datetime import datetime
import requests
import pyaudio
from piper import PiperVoice


import requests


def get_location(city=None):
    headers = {
        # Benutzerdefinierter User-Agent
        'User-Agent': 'MySmartHomeApp/1.0 (your_email@example.com)'
    }
    try:
        if city:
            url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Überprüft, ob der Statuscode 200 ist (erfolgreich)
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon'], city
            else:
                print("Keine Daten für die angegebene Stadt gefunden.")
        else:
            response = requests.get('http://ip-api.com/json/', headers=headers)
            response.raise_for_status()  # Überprüft, ob der Statuscode 200 ist (erfolgreich)
            data = response.json()
            return data['lat'], data['lon'], data['city']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP-Fehler aufgetreten: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Ein Fehler bei der Anfrage ist aufgetreten: {req_err}")
    except ValueError as json_err:
        print(f"Fehler beim Verarbeiten der JSON-Daten: {json_err}")
    except Exception as e:
        print(f"Ein allgemeiner Fehler ist aufgetreten: {e}")


def get_weather_forecast(city=None):
    try:
        latitude, longitude, city = get_location(city)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_weather = data['current_weather']
        temperatur = str(current_weather['temperature']).replace(".", "komma")

        if "-" in temperatur:
            tts(f"Die Temperatur in {city}: beträgt minus {temperatur}°Celsius")
            return True
        else:
            tts(f"Die Temperatur in {city}: beträgt {temperatur}°Celsius")
            return True
    except requests.RequestException as e:
        tts(f"Fehler beim Abrufen der Wetterdaten: {e}")
        return False
    except TypeError:
        tts("Tut mir Leid so einen Ort kann ich leider nicht finden")

# Guckt ob das Wort "in" bei einer Temperaturabfrage gekommen ist für ein bestimmten Ort
# und falls nicht, soll die Temperatur am momentanen Standort ausgegeben werden


def get_ort_für_temperaturabfrage(transkript):
    print("hat geklappt")
    wörter = transkript.split()
    for i, wort in enumerate(wörter):
        if wort.lower() == "in" and i + 1 < len(wörter):
            ort = wörter[i + 1]
            return get_weather_forecast(ort)
    else:
        return get_weather_forecast()


# Benutzt das Text to speech Modell von Thorsten um einen bestimmten Text verbal auszugeben


def get_current_time_for_tts():
    # Get the current time
    now = datetime.now()

    # Extract hours and minutes
    hours = now.hour
    minutes = now.minute

    # Format minutes correctly
    if minutes < 10:
        minutes_str = str(minutes)
    else:
        minutes_str = f"{minutes:02d}"

    # Return the formatted string
    return tts(f"Es ist {hours} Uhr {minutes_str}")


def tts(text):
    model_path = "tts_models/de_DE-thorsten-high.onnx"
    text_to_synthesize = str(text)
    voice = PiperVoice.load(model_path, use_cuda=False)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=voice.config.sample_rate,
                    output=True)
    for audio_bytes in voice.synthesize_stream_raw(
        text=text_to_synthesize,
        speaker_id=None,  # Optional: Ändern Sie die Sprecher-ID je nach Modell und Verfügbarkeit
        # Beeinflusst die Geschwindigkeit der Sprache (1.0 ist Standard)
        length_scale=1.0,
        # Beeinflusst die natürliche Variation der Stimme (0.667 für bessere Stabilität)
        noise_scale=0.667,
        # Beeinflusst die Klangfarbe (0.8 für ein gutes Gleichgewicht)
        noise_w=0.8,
        # Sekunden Stille nach jedem Satz (0.5 für natürlichere Pausen)
        sentence_silence=0.5,
    ):
        stream.write(audio_bytes)
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    # uhrzeit = get_current_time_for_tts()
    # get_weather_forecast("stuttgart")
    tts("kake ich nicht normal, bei so langen und vollen sätzen ab? ich bin verwirrt")
