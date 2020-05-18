from sense_hat import SenseHat
import time
import datetime
import smtplib
from common import emailer, chores, collect_facts
import threading
import subprocess
import random
import json
import os

# instatiate and clear the Sense Hat
sense = SenseHat()
sense.clear()
sense.low_light = True
sense.set_rotation(180)
EMAIL_ADRESSES_TXT = '/home/pi/Documents/home_chores_project/email_addresses.txt'

with open(EMAIL_ADRESSES_TXT) as json_file:
    EMAIL_ADDRESSES = json.load(json_file)

EMAIL_TIME_HOUR = 17
EMAIL_TIME_MINUTE = 13
SEND_EMAILS = True
EMAIL_SENT_TODAY = False
SCROLL_SPEED = (0.06)

RANDOM_EVENTS = ['Board Game', 'Book Club', 'Garden Time', 'Movie Time', 'You Decide', 'Craft Club', 'Party Game']


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
                        chore_message, _ = chores.get_chores()
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
                        rand_event = RANDOM_EVENTS[random.randint(0, len(RANDOM_EVENTS)-1)]
                        sense.show_message('Random event is: %s' % (rand_event), back_colour=BACK_COLOUR,
                                           text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    else:
                        pass
                    LAST = event.direction
                else:
                    ## double clicks ##
                    if event.direction == 'up':
                        sense.show_message('powering off...', text_colour=r, scroll_speed=SCROLL_SPEED)
                        time.sleep(10)
                        os._exit(1)
                        # subprocess.Popen(['sudo' 'shutdown', '-h', 'now'])
                    elif event.direction == 'down':
                        sense.show_message('For chores press down', back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    elif event.direction == 'left':
                        print('getting facts...')
                        fact = collect_facts.collect_facts()
                        sense.show_message(
                            fact, back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    elif event.direction == 'right':
                        sense.show_message('toggling emails. set to: %s ' %
                              (not SEND_EMAILS), back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED )
                        SEND_EMAILS = not SEND_EMAILS
                    elif event.direction == 'middle':
                        print('dance baby...')
                        dance_baby(sense)
                    else:
                        pass
                    LAST = 'a'
                

def make_email(sender, name, email_add, current_date):
    _, all_chores = chores.get_chores()  
    daily_chores = '<li> , '.join(['%s </li>']*len(all_chores['daily'][name[0]]))
    weekly_chores = '<li> , '.join(['%s </li>']*len(all_chores['weekly'][name[0]]))
    emailSubject = "Chores for %s" % (current_date)
    _, week_ending = chores.get_current_week_range()
    emailContent = "Hello %s! <br><br> Your Daily Chores for today are: <br> <ul> %s </ul>. <br><br> Chores which will \
        need to be completed by %s are: <br> <ul> %s </ul> <br><br> Raspberry Pi out." % (name, daily_chores, str(week_ending), weekly_chores)
    sender.sendmail('thomasjames.keel@googlemail.com', emailSubject, emailContent)
    print(name, 'sent!')
    return


def distribute_emails():
    global SEND_EMAILS, EMAIL_SENT_TODAY
    while True:
        if SEND_EMAILS:
            print('sending?')
            current_time = time.localtime()
            if current_time.tm_hour == EMAIL_TIME_HOUR and current_time.tm_min == EMAIL_TIME_MINUTE and not EMAIL_SENT_TODAY:
                print('actually sending')
                sense.show_message('sending emails',  back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                sender = emailer.Emailer()
                for name, email_add in EMAIL_ADDRESSES.items():
                    print(name, email_add)
                current_date = datetime.datetime.now().strftime('%d %b')
                make_email(sender, name, email_add, current_date)
                EMAIL_SENT_TODAY = True
            elif current_time.tm_hour == 1 and current_time.tm_min == 0:
                EMAIL_SENT_TODAY = False
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
    local_time = datetime.datetime.now().strftime('%d %b %H:%M')
    sense.show_message("Date: %s " % (local_time), back_colour=BACK_COLOUR,
                       text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
    return


def dance_baby(sense):
    return


# def end_program():
#     time.sleep(36)
#     os._exit(1)


if __name__ == "__main__":
    t1 = threading.Thread(target=watch_pi)
    t2 = threading.Thread(target=distribute_emails)
    # t3 = threading.Thread(target=end_program)
    t1.setDaemon(True)
    t2.setDaemon(True)
    # t3.setDaemon(True)
    t1.start()
    t2.start()
    # t3.start()
    while True:
        pass
