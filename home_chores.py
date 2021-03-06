#!/usr/bin/env python
# coding=utf-8
"""
    Description
    =====================
    Main application file. Runs a program for deciding who has chores today and then emails them with their list.
    
    Requirements
    ====================
    Raspberry Pi with SENSE HAT

    Joystick Functionality
    =====================
    DOWN : List all chores on rota and current assignee
    UP : Weather from SENSE HAT
    UP*2 : Stop program and exit 
    RIGHT : Random fact from uselessfacts API
    RIGHT*2: Toggle emails
    LEFT : Current date and time
    LEFT*2: Show controls
    MIDDLE : Random event chooser

    Operation Times:
    ======================
    Emailing:
        - will send emails at a given hour and minute (see EMAIL_TIME_HOUR & EMAIL_TIME_MINUTE)

    Powering off (to save energy):
        - will power off at a given time (see POWER_OFF_HOUR & POWER_OFF_MINUTE)


    Notes:
    ====================
    Email addresses will need to be stored in a seperate file within the Raspberry Pi's filesystem.
    Can be run using a crontab job on the Raspberry Pi e.g. @reboot python <PATH TO FILE>/home_chores.py &

"""
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

# set a random seed
random.seed(datetime.datetime.now())


# instatiate and clear the Sense Hat
sense = SenseHat()
sense.clear()
sense.low_light = True
sense.set_rotation(180)
EMAIL_ADRESSES_TXT = '/home/pi/Documents/home_chores_project/email_addresses.txt'

sense.show_message('Hello :)')

with open(EMAIL_ADRESSES_TXT, 'rb') as json_file:
    EMAIL_ADDRESSES = json.load(json_file)

EMAIL_TIME_HOUR = 7
EMAIL_TIME_MINUTE = 30
POWER_OFF_HOUR = 10
POWER_OFF_MINUTE = 1
SEND_EMAILS = True
EMAIL_SENT_TODAY = False
SCROLL_SPEED = (0.05)

RANDOM_EVENTS = ['Board Game', 'Book Club', 'Garden Time',
                 'Movie Time', 'You Decide', 'Craft Club', 'Party Game']


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
                        print('getting facts...')
                        fact = collect_facts.collect_facts()
                        sense.show_message(
                            fact, back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    elif event.direction == 'middle':
                        print('getting random event...')
                        rand_event = RANDOM_EVENTS[random.randint(
                            0, len(RANDOM_EVENTS)-1)]
                        sense.show_message('Random event is: %s' % (rand_event), back_colour=BACK_COLOUR,
                                           text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                    else:
                        pass
                    LAST = event.direction
                else:
                    ## FOR DOUBLE CLICKS ##
                    if event.direction == 'up':
                        # power off
                        sense.show_message(
                            'powering off...', text_colour=r, scroll_speed=SCROLL_SPEED)
                        time.sleep(10)
                        os._exit(1)
                    elif event.direction == 'down':
                        pass
                    elif event.direction == 'left':
                        # show controls
                        sense.show_message('Controls: U: Chores D: Weather L: Date R: Controls M: Random Event', back_colour=BACK_COLOUR,
                                            text_colour=TEXT_COLOUR, scroll_speed=(0.03))
                    elif event.direction == 'right':
                        # toggle emails
                        sense.show_message('toggling emails. set to: %s ' %
                                           (not SEND_EMAILS), back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                        SEND_EMAILS = not SEND_EMAILS
                    elif event.direction == 'middle':
                        print('dance baby...')
                        pass
                    else:
                        pass
                    LAST = 'a'
        time.sleep(5)
                


def make_email(sender, name, email_add, current_date):
    _, all_chores = chores.get_chores()
    fact = collect_facts.collect_facts()
    daily_chores = ("".join(['<li>%s</li>']*len(all_chores['daily']
                                                [name[0]]))) % tuple(all_chores['daily'][name[0]])
    weekly_chores = ("".join(['<li>%s</li>']*len(all_chores['weekly']
                                                 [name[0]]))) % tuple(all_chores['weekly'][name[0]])
    emailSubject = "Chores for %s" % (current_date)
    emailContent = "Hello %s! <br><br> Your Daily Chores for today are: <br> <ul> %s </ul> <br><br> Chores which will \
        need to be completed by this Sunday are: <br> <ul> %s </ul> <br><br>. Have a good day, <br>Raspberry Pi out. <br><br> Daily Fact: %s " % (name, daily_chores, weekly_chores, fact)
    sender.sendmail(email_add, emailSubject, emailContent)
    return


def distribute_emails():
    global SEND_EMAILS, EMAIL_SENT_TODAY
    while True:
        if SEND_EMAILS:
            current_time = time.localtime()
            if current_time.tm_hour == EMAIL_TIME_HOUR and current_time.tm_min == EMAIL_TIME_MINUTE and not EMAIL_SENT_TODAY:
                sense.show_message('sending emails',  back_colour=BACK_COLOUR,
                                   text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                chores.read_and_update_day_counter()
                sender = emailer.Emailer()
                for name in EMAIL_ADDRESSES.keys():
                    current_date = datetime.datetime.now().strftime('%d %b')
                    make_email(sender, name, EMAIL_ADDRESSES[name], current_date)
                sense.show_message('all emails sent',  back_colour=BACK_COLOUR,
                                   text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
                EMAIL_SENT_TODAY = True
            elif current_time.tm_hour == 1 and current_time.tm_min == 0:
                EMAIL_SENT_TODAY = False
            elif current_time.tm_hour == POWER_OFF_HOUR and current_time.tm_min == POWER_OFF_MINUTE:
                sense.show_message(
                    'powering off...', text_colour=r, scroll_speed=SCROLL_SPEED)
                time.sleep(10)
                os._exit(1)
            time.sleep(30)
            pass


def get_weather(sense):
    temp = sense.get_temperature()
    temp = round(temp, 1)
    humidity = sense.get_humidity()
    humidity = round(humidity, 1)
    pressure = sense.get_pressure()
    pressure = round(pressure, 1)
    sense.show_message("Temperature: %s.C  Humidity: %s%%  Pressure: %smb" % (temp, humidity, pressure),
                       back_colour=BACK_COLOUR, text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
    return


def get_date(sense):
    local_time = datetime.datetime.now().strftime('%d %b %H:%M')
    sense.show_message("Date: %s " % (local_time), back_colour=BACK_COLOUR,
                       text_colour=TEXT_COLOUR, scroll_speed=SCROLL_SPEED)
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
