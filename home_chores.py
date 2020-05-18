from sense_hat import SenseHat
import time
import datetime
import smtplib
from common import emailer, chores, collect_facts
import threading
import subprocess
import random

# instatiate and clear the Sense Hat
sense = SenseHat()
sense.clear()
sense.low_light = True
sense.set_rotation(180)

sender = emailer.Emailer()

EMAIL_ADDRESSES = {'Tom': 'thomasjames.keel@gmail.com', 'Freya': 'freyasienna.k@gmail.com',
                   'Mum': 'amandajane.keel@gmail.com', 'Jonathon': 'jonpage90@hotmail.com'}

EMAIL_TIME_HOUR = 8
EMAIL_TIME_MINUTE = 1
SEND_EMAILS = True
EMAIL_SENT_TODAY = False
SCROLL_SPEED = (0.08)

RANDOM_EVENTS = ['Board Game', 'Book Club', 'Garden Time', 'Movie Time', 'You Decide', 'Craft Club', 'Party Game']
# sendTo = 'thomasjames.keel@gmail.com'
# emailSubject = "Hello Tom"
# emailContent = "This is a test and you smell great goodbye!"

# # sender.sendmail(sendTo, emailSubject, emailContent)
# print('sent!')

r = (255, 0, 0)
b = (0, 100, 255)
y = (255, 255, 0)
g = (0, 255, 0)
n = (0, 0, 0)
t = (255, 50, 0)

BACK_COLOUR = n
TEXT_COLOUR = t
CURRENT = ''
LAST = 's'

def watch_pi():
    while True:
        global CURRENT, LAST, SEND_EMAILS
        for event in sense.stick.get_events():
            CURRENT = event.direction
            print(event.direction, event.action)
            print(CURRENT, LAST)
            if event.action == 'pressed':
                if CURRENT != LAST:
                    if event.direction == 'up':
                        print('getting weather...')
                        get_weather(sense)
                    elif event.direction == 'down':
                        print('getting chores...')
                        chore_message = chores.get_chores()
                        sense.show_message(chore_message, back_colour=BACK_COLOUR,
                                           text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    elif event.direction == 'left':
                        print('getting date...')
                        get_date(sense)
                    elif event.direction == 'right':
                        sense.show_message('Controls: U: Chores D: Weather L: Date R: Controls M: Random Event', back_colour=BACK_COLOUR,
                                           text_colour=TEXT_COLOUR, scroll_speed=(0.03))
                    elif event.direction == 'middle':
                        print('getting random event...')
                        rand_event = RANDOM_EVENTS[random.randint(1, len(RANDOM_EVENTS))]
                        sense.show_message('Random event is: %s' % (rand_event), back_colour=BACK_COLOUR,
                                           text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    else:
                        pass
                else:
                    ## double clicks ##
                    if event.direction == 'up':
                        sense.show_message('powering off...', text_colour=r, scroll_speed=SCROLL_SPEED)
                        time.sleep(10)
                        subprocess.Popen(['shutdown', '-h', 'now'])
                    elif event.direction == 'down':
                        pass
                    elif event.direction == 'left':
                        print('getting facts...')
                        fact = collect_facts.collect_facts()
                        sense.show_message(
                            fact, back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    elif event.direction == 'right':
                        sense.show_message('toggling emails... setting to: %s ' %
                              (not SEND_EMAILS), back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED )
                        SEND_EMAILS = not SEND_EMAILS
                    elif event.direction == 'middle':
                        print('dancing baby...')
                        dance_baby(sense)
                    else:
                        pass
                    LAST = 's'
                LAST = event.direction


def distribute_emails():
    global SEND_EMAILS
    while True:
        if SEND_EMAILS:
            current_time = time.localtime()
            if current_time.tm_hour == EMAIL_TIME_HOUR and current_time.tm_min == EMAIL_TIME_MINUTE and not EMAIL_SENT_TODAY:
                print('the time')
                EMAIL_SENT_TODAY = True
            elif current_time.tm_hour == 1 and current_time.tm_min == 0:
                EMAIL_SENT_TODAY = False
                # DAY_COUNTER =+ 1 ??
            print('sending email!')
            time.sleep(30)
            pass


def get_weather(sense):
    temp = sense.get_temperature()
    temp = round(temp, 1)
    humidity = sense.get_humidity()
    humidity = round(humidity, 1)
    pressure = sense.get_pressure()
    pressure = round(pressure, 1)
    sense.show_message("Temperature: %s.C  Humidity: %s%%  Pressure: %s mb" % (temp, humidity, pressure),
                       back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
    return


def get_date(sense):
    local_time = datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')
    sense.show_message("Date: %s " % (local_time), back_colour=BACK_COLOUR,
                       text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
    return


def dance_baby(sense):
    return


if __name__ == "__main__":
    t1 = threading.Thread(target=watch_pi)
    t2 = threading.Thread(target=distribute_emails)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass
