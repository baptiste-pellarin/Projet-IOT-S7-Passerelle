import math
import threading, serial, socket
from time import time

result = (0,0,0,)


def send_data(data):
    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        ser.write(bytes(data, "UTF-8"))


def lecture():
    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        line = ser.readline()
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
                    temperature,
                    lux,
                    timestamp,
                )


msg = str.encode("Hello Client!")
# Créer une socket datagramme
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Lier à l'adresse IP et le port
s.bind(("0.0.0.0", 10001))
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

    if message == "1":
        send_data("LT")
    elif message == "2":
        send_data("TL")
    else:
        result_tmp: tuple = lecture()
        if result_tmp:
            result = result_tmp
            print(";".join(result), "updated")
            s.sendto(bytes(";".join(result), "UTF-8"), address)
        else:
            print(";".join(result), "old")
            s.sendto(bytes(";".join(result), "UTF-8"), address)
