""""
La raspberry ne peut pas faire tourner InfluxDB
"""
import json
import socket
import time as tm

from utils import root_logger

class_logger = root_logger.getChild("telegraf")


class Telegraf:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_data(self, temperature, lumens, no_capteur, time=None):
        data = json.dumps(
            {'no_capteur': no_capteur, "temperature": temperature, "lumens": lumens, "time": time or tm.time()})
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(bytes(data, "UTF-8"),
                        (self.host, self.port,))
            class_logger.info("Envoie des données à telegraf")
            class_logger.info(data)
        except socket.error as e:
            class_logger.error(f"Erreur de socket: {e}")
