import requests
import pyaudio
from piper import PiperVoice


def get_location(city=None):
    try:
        if city:
            # Verwende Nominatim Geocoding API
            url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
            response = requests.get(url)
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon'], city
        else:
            # Verwende IP-Geolokalisierung, wenn kein Städtenamen angegeben ist
            response = requests.get('http://ip-api.com/json/')
            data = response.json()
            return data['lat'], data['lon'], data['city']
    except:
        tts("Tut mir leid, so einen Ort kann ich leider nicht finden")


def get_weather_forecast(city=None):
    # Open-Meteo API-Endpunkt für Wettervorhersagen
    try:
        latitude, longitude, city = get_location(city)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        response = requests.get(url)
        # Löst eine Ausnahme aus, wenn der HTTP-Statuscode ein Fehler ist (4xx oder 5xx)
        response.raise_for_status()

        # Konvertiert die Antwort in ein Python-Dictionary
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


def get_ort_für_temperaturabfrage(transkript):
    wörter = transkript.split()

    # Durchsuche das Transkript nach dem Schlüsselwort "in" und nimm das folgende Wort als Ortsnamen
    for i, wort in enumerate(wörter):
        if wort.lower() == "in" and i + 1 < len(wörter):
            ort = wörter[i + 1]
            return get_weather_forecast(ort)

    else:
        return get_weather_forecast()


def tts(text):
    model_path = "tts_models/de_DE-thorsten-high.onnx"
    text_to_synthesize = str(text)

    # Laden der PiperVoice-Instanz mit dem angegebenen Modell
    voice = PiperVoice.load(model_path, use_cuda=False)

    # Initialisieren von PyAudio
    p = pyaudio.PyAudio()

    # Öffnen des Audio-Streams
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=voice.config.sample_rate,
                    output=True)

    # Generieren und Abspielen des Audio-Streams
    for audio_bytes in voice.synthesize_stream_raw(
        text=text_to_synthesize,
        speaker_id=None,  # Optional: Spezifizieren Sie die Sprecher-ID, falls benötigt
        length_scale=1.0,  # Optional: Anpassen der Länge
        noise_scale=1.0,  # Optional: Anpassen des Rauschens
        noise_w=1.0,  # Optional: Anpassen des Rauschens weiter
        sentence_silence=0.5,  # Sekunden Stille nach jedem Satz
    ):
        stream.write(audio_bytes)

    # Stream schließen
    stream.stop_stream()
    stream.close()

    # PyAudio beenden
    p.terminate()
