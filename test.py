import time
import threading as th
from sense_hat import SenseHat

sense = SenseHat()


def message_shower(message):
    global sense
    sense.show_message(message)


def show_message_background(message):
    th.Thread(target=message_shower, args=(message,)).start()


show_message_background("my name is Dave")

while True:
    print("sleeping...")
    time.sleep(1)
