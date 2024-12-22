import pyaudio
import wave
import audioop
from collections import deque
import whisper


def record_audio():
    """
    Nimmt ein Wort oder mehrere Worte vom Mikrofon auf und
    gibt die Daten als ein Array von signierten Shorts zurück.
    """

    # PyAudio initialisieren
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100,
                    input=True, frames_per_buffer=1024)  # Öffnet den Audiostream mit spezifischen Parametern
    print("Please speak. Recording will start when you speak.")
    audio2send = []  # Liste zum Speichern der aufgenommenen Audio-Daten
    cur_data = ''  # Variable für das aktuelle Audio-Datenstück
    rel = 44100 / 1024  # Verhältnis zur Berechnung der Fenstergröße
    # Verschiebefenster zur Überwachung der Lautstärke
    slid_win = deque(maxlen=int(2 * rel))
    started = False  # Flag, das anzeigt, ob die Aufnahme gestartet wurde
    threshold = 500  # Schallpegel-Schwelle, um festzustellen, ob jemand spricht

    while True:
        # Liest 1024 Byte (Samples) von der Audioquelle
        cur_data = stream.read(1024)
        # Berechnet den maximalen Pegel und fügt ihn dem Fenster hinzu
        slid_win.append(audioop.max(cur_data, 2))
        # Prüft, ob der Schallpegel die Schwelle überschreitet
        if sum([1 for x in slid_win if x > threshold]) > 0:
            if not started:
                print("Recording...")
                started = True  # Setzt das Flag auf True, wenn die Aufnahme startet
            # Fügt das aktuelle Datenstück der Liste hinzu
            audio2send.append(cur_data)
        elif started:
            print("Finished recording.")
            break  # Beendet die Schleife und somit die Aufnahme, wenn die Schwelle nicht mehr überschritten wird

    stream.close()  # Schließt den Audio-Stream
    p.terminate()  # Beendet PyAudio

    # Speichert die aufgenommenen Daten als WAV-Datei
    # Öffnet eine neue WAV-Datei zum Schreiben
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(1)  # Setzt die Anzahl der Kanäle auf 1 (Mono)
    # Setzt die Sample-Breite auf 16 Bit
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)  # Setzt die Abtastrate auf 44,1 kHz
    # Schreibt die aufgenommenen Audio-Daten in die Datei
    wf.writeframes(b''.join(audio2send))
    wf.close()  # Schließt die WAV-Datei

    # Transkribiert die Audio-Datei und gibt den transkribierten Text zurück
    return audio_transcribe("output.wav")


def audio_transcribe(audio_file):
    # Lädt das Whisper-Spracherkennungsmodell
    model = whisper.load_model("tiny")
    audio = whisper.load_audio(audio_file)  # Lädt die Audio-Datei
    # Passt die Länge des Audios an (falls erforderlich)
    audio = whisper.pad_or_trim(audio)
    # Konvertiert das Audio in ein Mel-Spektrogramm
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # Setzt die Decodierungsoptionen (hier: Deutsch)
    options = whisper.DecodingOptions(fp16=False, language="de")
    # Dekodiert das Mel-Spektrogramm in Text
    result = whisper.decode(model, mel, options)
    print(result)  # Gibt das Ergebnis auf der Konsole aus

    text = result.text.lower().strip(",").strip(
        ".")  # Bereinigt den transkribierten Text
    return text  # Gibt den bereinigten Text zurück
