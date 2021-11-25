#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021

import configparser
import multiprocessing as mp

from models import SerialConn, UDPServer, InfluxDBConn, PeriodicCheck
from utils import root_logger

main_logger = root_logger.getChild("main")

if __name__ == "__main__":
    main_logger.info("Initialisation des sémaphores et de la Queue")

    serial_queue = mp.Queue(maxsize=1)
    udp_queue = mp.Queue(maxsize=1)

    mutex_serial = mp.Semaphore(0)
    mutex_udp = mp.Semaphore(0)

    main_logger.info("Lecture de la configuration")
    configuration = configparser.ConfigParser()
    configuration.read("config.cfg")

    main_logger.info("Initialisation de la connexion à InfluxDB")
    influxdb_conn = InfluxDBConn(
        configuration["INFLUXDB"]["URL"], configuration["INFLUXDB"]["TOKEN"], configuration["INFLUXDB"]["DATABASE"]
    )

    main_logger.info("Initialisation du serveur UDP")
    udp_server = UDPServer(
        serial_queue,
        udp_queue,
        mutex_serial,
        mutex_udp,
        host=configuration["SERVER"]["HOST"],
        port=configuration["SERVER"]["PORT"],
    )

    main_logger.info("Initialisation de la lecture série")
    serial_conn = SerialConn(
        serial_queue,
        udp_queue,
        mutex_serial,
        mutex_udp,
        influxdb_conn,
        ttydir=configuration["SERIAL"]["DIR"],
        ttyspeed=configuration["SERIAL"]["SPEED"],
    )

    main_logger.info("Initialisation de la recharge périodique")
    periodic = PeriodicCheck(mutex_serial, serial_queue)

    main_logger.info("Initialisation terminée")

    main_logger.info("Démarrage des threads")

    thread_udp = mp.Process(target=udp_server.server)
    thread_serial_read = mp.Process(target=serial_conn.lecture)
    thread_serial_write = mp.Process(target=serial_conn.ecriture)
    thread_periodic = mp.Process(target=periodic.run)

    thread_udp.start()
    thread_serial_read.start()
    thread_serial_write.start()
    thread_periodic.start()

    thread_udp.join()
    thread_serial_read.join()
    thread_serial_write.join()
    thread_periodic.join()
