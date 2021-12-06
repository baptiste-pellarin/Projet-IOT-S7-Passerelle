""""
La raspberry ne peut pas faire tourner InfluxDB
"""
import json
import random
import socket
import time as tm

from utils import root_logger

class_logger = root_logger.getChild("telegraf")


class Telegraf:
    """
    Connexion au socket udp telegraf
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.capitals = json.loads(open("./country-capitals.json", "r").read())  # Données pour simuler que les capteurs sont dans plusieurs pays

    def send_data(self, temperature, lumens, no_capteur, time=None):

        data = self.get_influx_query(temperature, lumens, no_capteur, fake_data=True)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Connexion au socket telegraf
            sock.sendto(
                bytes(data, "UTF-8"),
                (
                    self.host,
                    self.port,
                ),
            )
            class_logger.info("Envoie des données à telegraf")
            class_logger.info(data)
        except socket.error as e:
            class_logger.error(f"Erreur de socket: {e}")

    def get_influx_query(self, temperature, lumens, no_capteur, fake_data=False) -> str:
        capteur = {"code": None, "lat": None, "long": None}
        if fake_data:
            country = random.choice(self.capitals)  # Récupération des coordonnées d'un pays au hasard dans la liste
            capteur["code"] = country.get("CountryCode")
            capteur["lat"] = float(country.get("CapitalLatitude", 0))
            capteur["long"] = float(country.get("CapitalLongitude", 0))

            return f"data_capteurs,no_capteur={capteur['code']} temperature={temperature}i,lumens={lumens}i,no_capteur=\"{capteur['code']}\",lat={capteur['lat']},long={capteur['long']} {int(tm.time_ns())}"
        else:
            return f'data_capteurs,no_capteur={no_capteur} temperature={temperature}i,lumens={lumens}i,no_capteur="{no_capteur}" {int(tm.time_ns())}'
