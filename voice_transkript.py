from shelly_plug_s_ansteuerung import shelly_turn_off, shelly_turn_on
import simpleaudio as sa
from funktionen import get_ort_für_temperaturabfrage
import re
from funktionen import tts
from voice_catching import record_audio


"""def play_sound(file):
    wave_obj = sa.WaveObject.from_wave_file(file)
    play_obj = wave_obj.play()
    play_obj.wait_done()"""


# Überprüft das Transkript, ob der Nutzer ein Befehl aufgeben will
def frage(transkript):
    if "hallo zimmer" in transkript:
        tts("Wie kann ich dir helfen?")
        return True
    else:
        return False


Licht_an_SW = ["licht an", "lampe an", "licht auf"]
Licht_aus_SW = ["licht aus", "lampe aus", "licht aus"]
temperatur = "temperatur|grad|wetter|grat"
nachsprechen = ["nach sprechen"]

# Durchsucht das Transkript nach bestimmten Worten, die ein Befehl auslösen


def befehl_umsetzung(transkript):
    if any(wort in transkript for wort in Licht_an_SW):
        tts("Mach ich")
        shelly_turn_on()
        return True
    elif any(wort in transkript for wort in Licht_aus_SW):
        tts("Mach ich")
        shelly_turn_off()
        return True
    elif re.search(temperatur, transkript):
        get_ort_für_temperaturabfrage(transkript)
        return True
    elif any(wort in transkript for wort in nachsprechen):
        tts("ja kann ich machen")
        text = record_audio()
        tts(text)
    else:
        tts("Kannst du es bitte nochmal wiederholen?")
        return False
