#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021

import multiprocessing as mp
import socket

from utils import root_logger

class_logger = root_logger.getChild("udp_sever")


class UDPServer:
    def __init__(
        self,
        serial_queue: mp.Queue,
        udp_queue: mp.Queue,
        mutex_serial: mp.Semaphore,
        mutex_udp: mp.Semaphore,
        host: str,
        port=10000,
    ):
        """

        :param serial_queue: Queue avec les informations récupérées sur la liaison série
        :param udp_queue: Queue avec les commandes envoyées à la liaison série depuis le serveurs UDP
        :param mutex_serial: Verrouillage de la lecture quand il n'y a pas besoin
        :param mutex_udp: Verrouillage des demandes UDP quand une requête est déjà en cours
        :param host: Interface d'écoute
        :param port: Port d'écoute
        """

        self.serial_queue: mp.Queue = serial_queue
        self.udp_queue: mp.Queue = udp_queue

        self.host: str = host
        self.port: int = int(port)
        self.datagram_size: int = 1024

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.mutex_serial: mp.Semaphore = mutex_serial
        self.mutex_udp: mp.Semaphore = mutex_udp

    def server(self):
        self.udp_socket.bind(
            (
                self.host,
                self.port,
            )
        )

        class_logger.info(
            "Écoute sur l'adresse %s:%s"
            % (
                self.host,
                self.port,
            )
        )

        while True:
            data = self.udp_socket.recvfrom(self.datagram_size)
            if len(data) == 2:
                client_message = data[0]
                client_host = data[1]

                class_logger.info(
                    "Message reçu de l'hôte %s :\n %s "
                    % (
                        client_host,
                        client_message,
                    )
                )

                client_message = str(client_message, "UTF-8")
                client_message = client_message.strip("\n")

                if client_message == "1":
                    self.udp_queue.put("LT\r\n")  # On envoie "LT" sur la liaison série
                    self.send_data(client_host, ("LT",))
                elif client_message == "2":
                    self.udp_queue.put("TL\r\n")
                    self.send_data(client_host, ("TL",))
                elif client_message == "3":
                    self.mutex_serial.release()  # On autorise la lecture sur le port série
                    self.mutex_udp.acquire()  # On empêche les autres requêtes UDP tant que celle-ci n'a pas été traitée
                    result = self.serial_queue.get()  # On récupère le résultat de la demande sur la liaison série
                    class_logger.info("Information reçu depuis TTY : \n%s" % " ".join(result))
                    self.send_data(client_host, result)  # On revoie le résultat au client

                else:
                    class_logger.warn("Message inconnu : %s" % client_message)

            else:
                class_logger.warn("Packet non conforme")

    def send_data(self, address: tuple, data: tuple):
        class_logger.info("Envoie des informations à %s:\n%s" % (address, data))
        self.udp_socket.sendto(bytes(";".join(data), "UTF-8"), address)
