import datetime
import random
import string

import math
import serial, socket

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

result = (0, 0, 0,)

TEST = True

from datetime import datetime, timedelta

# You can generate an API token from the "API Tokens Tab" in the UI
token = "RJ1s-1MxDeAdhyY7XDN7Gzk--gYb1SdWUJIAYflLNEhBA5C6x82RB_KZjyWy66ymJjGFBCPvREFYT41EQs31Qw=="
org = "iot_org"
bucket = "iot_bucket"

client = InfluxDBClient(url="http://192.168.152.200:8086", token=token, org=org)


def send_data(data):
    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        ser.write(bytes(data, "UTF-8"))


def lecture():
    if TEST:
        return str(random.randint(20, 35)), str(random.randint(90, 120)),

    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        line = ser.readline()
        print(line)
        global temperature, lux
        string_encoded = bytes(line).decode("UTF-8")

        if string_encoded[0] == "I":
            string_encoded = string_encoded[2:]  # Retrait du codage
            string_encoded = string_encoded[:-2]  # Retrait des \r\n
            data = string_encoded.split(";")

            if len(data) == 2:
                temperature = data[0] or 0
                lux = data[1] or 0

                return (
                    str(temperature),
                    str(lux)
                )


def write_influxdb(temp, lux):
    no_capteur = ""

    for _ in range(2): no_capteur += random.choice(string.ascii_uppercase)

    point = Point("data_capteurs") \
        .tag("capteur_no", no_capteur) \
        .field("capteur_no", no_capteur) \
        .field("temperature", int(temp)) \
        .field("lumens", int(lux)) \
        .time(datetime.utcnow() - timedelta(seconds=random.randint(10, 5000)), WritePrecision.NS)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    write_api.write(bucket, org, point)
    # print("Résultat ajouté : ID %s" % result_mongo.inserted_id)


if __name__ == '__main__':

    msg = str.encode("Hello Client!")
    # Créer une socket datagramme
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Lier à l'adresse IP et le port
    s.bind(("0.0.0.0", 10000))
    print("Serveur UDP à l'écoute")
    # Écoutez les datagrammes entrants
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
            for _ in range(random.randint(10, 500)):
                # print(result)
                result: tuple = lecture()
                write_influxdb(result[0], result[1])
                # print(";".join(result), "updated")
                # s.sendto(bytes(";".join(result), "UTF-8"), address)
