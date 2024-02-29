from voice_transkript import frage, befehl_umsetzung
from voice_catching import record_audio


hallo = True
befehl = False
while hallo == True:
    transkript = record_audio()
    if frage(transkript) == True:
        befehl = False
        while befehl == False:
            befehl_transkript = record_audio()
            befehl = befehl_umsetzung(befehl_transkript)
