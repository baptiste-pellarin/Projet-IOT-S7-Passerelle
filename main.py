import threading, serial
from time import time


from flask import Flask, request

app = Flask("Passerelle_IoT")

temperature = lux = timestamp = None


@app.route("/")
def get_data():
    threading.Thread(target=lecture).start()

    global lux, temperature
    return {"temp": temperature, "lux": lux, "epoch": timestamp}


def send_data(data):
    with serial.Serial("/dev/ttyACM0", 115200) as ser:
        ser.write(bytes(data, "UTF-8"))


@app.route("/command", methods=["POST"])
def send_command():
    print(request.form)
    if request.form.get("command") == "TL" or request.form.get("command") == "LT":
        threading.Thread(target=send_data, args=(request.form.get("command"),)).start()
        return {"status": "OK"}

    return {"error": "Merci de faire une requête CORRECTE!"}, 400


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
                temperature = int(data[0] or 0)
                lux = int(data[1] or 0)
                timestamp = int(time())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
