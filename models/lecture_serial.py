#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021

import multiprocessing as mp

import serial

from utils import root_logger

class_logger = root_logger.getChild("lecture_serial")


class SerialConn:
    """
    Connexion au port série
    Récupération des informations capteurs
    Envoie les changements d'état

    """

    def __init__(
        self,
        serial_queue: mp.Queue,
        udp_queue: mp.Queue,
        mutex_serial: mp.Semaphore,
        mutex_udp: mp.Semaphore,
        influxdb_conn,
        ttydir: str,
        ttyspeed=11500,
    ):
        """

        :param serial_queue: Queue avec les informations récupérées sur la liaison série
        :param udp_queue: Queue avec les commandes envoyées à la liaison série depuis le serveurs UDP
        :param mutex_serial: Verrouillage de la lecture quand il n'y a pas besoin
        :param mutex_udp: Verrouillage des demandes UDP quand une requête est déjà en cours
        :param influxdb_conn: Classe pour utiliser InfluxDB
        :param ttydir: Fichier TTY (/dev/tty1..)
        :param ttyspeed: Vitesse de la liaison série en bauds/s
        """

        self.ttydir: str = ttydir
        self.ttyspeed: int = ttyspeed

        self.serial_queue: mp.Queue = serial_queue
        self.udp_queue: mp.Queue = udp_queue

        self.mutex_serial: mp.Semaphore = mutex_serial
        self.mutex_block_serial: mp.Semaphore = mp.Semaphore(1)
        self.mutex_udp: mp.Semaphore = mutex_udp

        self.influxdb_conn = influxdb_conn

        self.serial_conn = serial.Serial(self.ttydir, self.ttyspeed)

    def lecture(self):
        while True:
            self.mutex_serial.acquire()  # On attend que un process nous demande de lire sur la liaison

            class_logger.info("Attente de données")
            self.serial_conn.flushInput()  # On retire les informations n'ayant pas été collectées
            line = self.serial_conn.readline()  # On attend que le TTY nous donne des informations
            self.mutex_block_serial.acquire()  # On empêche l'utilisation de la liaison série

            class_logger.info("Lecture des données")
            #  ligne codée en UTF-8 de cette façon : I TEMP;LUX\r\n
            string_encoded = bytes(line).decode("UTF-8")

            if string_encoded[0] == "I":
                string_encoded = string_encoded[2:]  # Retrait du codage
                string_encoded = string_encoded[:-2]  # Retrait des \r\n
                data = string_encoded.split(";")

                if len(data) == 3:
                    temperature = data[0] or 0
                    lumens = data[1] or 0
                    no_capteur = data[2] or "UNK"

                    class_logger.info(
                        "Temprature : %s\nLumens : %s\nN° Capteur: %s" % (temperature, lumens, no_capteur)
                    )

                    mp.Process(
                        target=self.influxdb_conn.send_data,
                        args=(
                            temperature,
                            lumens,
                            no_capteur,
                        ),
                    ).start()  # On envoie les données à InfluxDB

                    self.serial_queue.put(
                        (
                            temperature,
                            lumens,
                            no_capteur,
                        )
                    )  # On ajoute le résultat à la queue des résultats
                    self.mutex_udp.release()  # On autorise les nouvelles requêtes UDP
            else:
                class_logger.warn("Donnée illisible : \n%s" % string_encoded)

            self.mutex_block_serial.release()  # On autorise l'utilisation de la liaison série

    def ecriture(self):
        while True:
            class_logger.info("Ecoute demande ecriture")
            message = self.udp_queue.get()  # On récupère le message présent dans la queue des messages UDP

            self.mutex_block_serial.acquire()  # On empêche l'utilisation de la liaison série

            self.serial_conn.write(bytes(message[:-2], "UTF-8"))
            class_logger.info("Ecriture : %s" % message)

            self.mutex_block_serial.release()  # On autorise l'utilisation de la liaison série
