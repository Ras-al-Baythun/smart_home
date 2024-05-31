from voice_transkript import frage, befehl_umsetzung
from voice_catching import record_audio

hallo = True
befehl = False
while hallo == True:
    transkript = record_audio()  # Nimmt Audio auf und transkribiert es
    print(transkript)
    if frage(transkript) == True:  # Überprüft, ob der Benutzer "hallo zimmer" gesagt hat
        befehl = False
        while befehl == False:
            befehl_transkript = record_audio()  # Nimmt weiteren Befehl auf
            befehl = befehl_umsetzung(befehl_transkript)  # Setzt den Befehl um
