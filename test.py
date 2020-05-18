import time
import threading as th
from sense_hat import SenseHat

sense = SenseHat()


def message_shower(message):
    global sense
    sense.show_message(message)


def show_message_background(message):
    th.Thread(target=message_shower, args=(message,)).start()


while True:
    print("sleeping...")
    show_message_background("my name is Dave")
    time.sleep(5)
    sense.clear()
    
