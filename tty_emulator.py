#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021
#

import random
import string

import serial
from time import sleep

"""
Fonctionne grace à tty0tty
https://github.com/freemed/tty0tty
"""

if __name__ == "__main__":
    with serial.Serial("/dev/tnt1", 115200) as ser:

        while True:
            no_capteur = ""
            for _ in range(2):
                no_capteur += random.choice(string.ascii_uppercase)
            temperature = str(random.randint(10, 30))
            lumens = str(random.randint(0, 100))
            sleep(1)
            ser.write(bytes(f"I {temperature};{lumens};{no_capteur}\r\n", "UTF-8"))
            print(f"I {temperature};{lumens};{no_capteur}")
