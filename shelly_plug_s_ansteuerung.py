import requests

# Ersetzen Sie dies mit der IP-Adresse Ihres Shelly Plug S
shelly_ip = "192.168.2.225"


def shelly_turn_on():
    url = f"http://{shelly_ip}/relay/0?turn=on"
    requests.get(url)


def shelly_turn_off():
    url = f"http://{shelly_ip}/relay/0?turn=off"
    requests.get(url)


if __name__ == "__main__":
    # Zum Einschalten
    shelly_turn_on()

    # Zum Ausschalten
    # shelly_turn_off()
