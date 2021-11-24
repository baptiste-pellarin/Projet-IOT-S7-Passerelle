import configparser

import math
import os, serial, socket

from datetime import datetime

import psycopg2
from time import time

configuration = configparser.ConfigParser()
configuration.read("config.cfg")

result = (0, 0, 0,)
conn = psycopg2.connect(f"dbname={configuration['DB']['NAME']} user={configuration['DB']['USER']} password={configuration['DB']['PASSWORD']} host={configuration['DB']['HOST']}")


def send_data(data):
    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        ser.write(bytes(data, "UTF-8"))


def lecture():
    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        line = ser.readline()
        print(line)
        global temperature, lux, timestamp
        string_encoded = bytes(line).decode("UTF-8")

        if string_encoded[0] == "I":
            string_encoded = string_encoded[2:]  # Retrait du codage
            string_encoded = string_encoded[:-2]  # Retrait des \r\n
            data = string_encoded.split(";")

            if len(data) == 2:
                temperature = str(data[0] or 0)
                lux = str(data[1] or 0)
                timestamp = str(math.floor(time()))

                return (
                    str(temperature),
                    str(lux),
                    str(timestamp),
                )


def write_postgres(temp, lux, conn):
    cur = conn.cursor()

    cur.execute(f"INSERT INTO capteurs_data VALUES (CURRENT_TIMESTAMP(10), 1, {temp}, {lux})")
    conn.commit()
    cur.close()


if __name__ == '__main__':

    msg = str.encode("Hello Client!")
    # Créer une socket datagramme
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Lier à l'adresse IP et le port
    s.bind(("0.0.0.0", 10000))
    print("Serveur UDP à l'écoute")
    # Écoutez les datagrammes entrants
    print("OK Influx")
    while True:
        addr = s.recvfrom(1024)
        message = addr[0]
        address = addr[1]
        clientMsg = "Message du client: {}".format(message)
        clientIP = "Adresse IP du client: {}".format(address)
        print(clientMsg)
        print(clientIP)
        # Envoi d'une réponse au client
        message = str(message, "UTF-8")
        message = message.strip("\n")
        print(message)

        if message == "1":
            print("LT")
            send_data("LT")
        elif message == "2":
            send_data("TL")
        else:
            print(result)
            result_tmp: tuple = lecture()
            if result_tmp and isinstance(result_tmp[0], str):
                result = result_tmp
                print(";".join(result), "updated")
                write_postgres(result[0], result[1], conn)
                s.sendto(bytes(";".join(result), "UTF-8"), address)
            elif isinstance(result[0], str):
                print(";".join(result), "old")
                s.sendto(bytes(";".join(result), "UTF-8"), address)
