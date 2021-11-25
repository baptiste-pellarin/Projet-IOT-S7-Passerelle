#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021

import multiprocessing as mp
from time import sleep

from utils import root_logger

class_logger = root_logger.getChild("periodic_check")


class PeriodicCheck:
    """
    Récupération périodique des données même si personne ne les demandes
    """

    def __init__(self, mutex_serial: mp.Semaphore, serial_queue: mp.Queue):
        """

        :param mutex_serial: Déverrouillage du mutex série
        :param serial_queue: On vide la queue de données série (SerialCOnn se charge de les envoyées sur InfluxDB)
        """
        self.mutex_serial: mp.Semaphore = mutex_serial
        self.serial_queue: mp.Queue = serial_queue

    def run(self):
        while True:
            sleep(10)
            class_logger.info("Demande nouvelles données")
            self.mutex_serial.release()
            self.serial_queue.get()
