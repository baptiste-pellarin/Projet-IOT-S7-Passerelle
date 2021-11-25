#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from utils import root_logger

class_logger = root_logger.getChild("influxdb")


class InfluxDBConn:
    """
    Connexion à InfluxDB et transmission des données

    """

    def __init__(self, url: str, token: str, database: str):
        """

        :param url: Url de l'instance
        :param token: Token d'authentification
        :param database: Base de données à utiliser
        """
        self._database: str = database

        self._client = InfluxDBClient(url=url, token=token)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def send_data(self, temperature, lumens, no_capteur, time=None):
        point = (
            Point("data_capteurs")
            .tag("no_capteur", no_capteur)
            .field("no_capteur", no_capteur)
            .field("temperature", int(temperature))
            .field("lumens", int(lumens))
            .time(time or datetime.utcnow(), WritePrecision.NS)
        )

        self._write_api.write(self._database, "-", point)

        class_logger.info(
            "Sauvegarde dans influxDB (db = %s):\nNo Capteur: %s\nTemperature: %s\nLumens: %s"
            % (
                self._database,
                no_capteur,
                temperature,
                lumens,
            )
        )
