from shelly_plug_s_ansteuerung import shelly_turn_off, shelly_turn_on
import simpleaudio as sa
from funktionen import get_ort_für_temperaturabfrage, get_current_time_for_tts
import re
from funktionen import tts
from voice_catching import record_audio
import torch
from transformers import BertTokenizer, BertForSequenceClassification


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


# Verzeichnis, in dem das trainierte Modell und der Tokenizer gespeichert sind
model_dir = './intent_model'

# Tokenizer und Modell laden
tokenizer = BertTokenizer.from_pretrained(model_dir)
model = BertForSequenceClassification.from_pretrained(model_dir)

# Labels-Wörterbuch, das während des Trainings verwendet wurde
label_dict = {
    1: "light_on",
    2: "light_off",
    3: "temperature",
    4: "repeat_after_me",
    5: "current_time"
}

# Funktionsdefinitionen


def shelly_turn_on():
    shelly_turn_on


def shelly_turn_off():
    shelly_turn_off


def repeat_after_me(message):
    tts(message)


"""def temperaturabfrage(transkript):
    get_ort_für_temperaturabfrage(transkript)"""


"""def record_audio():
    return "Dies ist ein aufgezeichneter Text"


def get_current_time_for_tts():
    print("Aktuelle Uhrzeit ausgeben")"""

# Funktion zur Vorhersage des Intents


def predict_intent(text):
    inputs = tokenizer(text, return_tensors='pt',
                       truncation=True, padding=True, max_length=128)
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    predicted_class_idx = probs.argmax().item()
    confidence = probs.max().item()
    if confidence < 0.75:
        return 0
    return predicted_class_idx


# Dictionary zur Zuordnung von Intents zu Funktionen
intent_functions = {
    1: lambda: (tts("Mach ich"), shelly_turn_on()),
    2: lambda: (tts("Mach ich"), shelly_turn_off()),
    3: lambda transkript: get_ort_für_temperaturabfrage(transkript),
    4: lambda: (tts("ja kann ich machen"), tts(record_audio())),
    5: lambda: get_current_time_for_tts()
}

# Hauptfunktion zur Verarbeitung des Transkripts


def befehl_umsetzung(transkript):
    intent = predict_intent(transkript)
    if intent == 0:
        tts("Kannst du es bitte nochmal wiederholen?")
        return False
    else:
        if intent == 3:
            intent_functions[intent](transkript)
        else:
            intent_functions[intent]()
        return True


"""Licht_an_SW = ["licht an", "lampe an", "licht auf"]
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
    elif "uhrzeit":
        get_current_time_for_tts()
    else:
        tts("Kannst du es bitte nochmal wiederholen?")
        return False
"""
