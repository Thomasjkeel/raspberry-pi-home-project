print('hello')
from sense_hat import SenseHat
import time
import smtplib
from common import emailer, chores, collect_facts
import threading
import subprocess

# instatiate and clear the Sense Hat
sense = SenseHat()
sense.clear()

sender = emailer.Emailer()

EMAIL_ADDRESSES = {'Tom':'thomasjames.keel@gmail.com', 'Freya':'freyasienna.k@gmail.com',\
                    'Mum':'amandajane.keel@gmail.com', 'Jonathon': 'jonpage90@hotmail.com'}

EMAIL_TIME_HOUR = 8
EMAIL_TIME_MINUTE = 1
SEND_EMAILS = True
EMAIL_SENT_TODAY = False

# sendTo = 'thomasjames.keel@gmail.com'
# emailSubject = "Hello Tom"
# emailContent = "This is a test and you smell great goodbye!"

# # sender.sendmail(sendTo, emailSubject, emailContent)
# print('sent!')

def watch_pi():
    while True:
        CURRENT = ''
        LAST = '_'
        for event in sense.stick.get_events():
            CURRENT = event.direction
            print(event.direction, event.action)
            if event.action == 'pressed':
                if CURRENT != LAST:
                    if event.direction == 'up':
                        print('getting weather...')
                        get_weather(sense)
                    elif event.direction == 'down':
                        print('getting chores...')
                        chore_message = chores.get_chores()
                        sense.show_message(chore_message)
                    elif event.direction == 'left':
                        print('getting date...')
                        get_date(sense)
                    elif event.direction == 'right':
                        print('getting facts...')
                        fact = collect_facts.collect_facts()
                        sense.show_message(fact)
                    elif event.direction == 'middle':
                        print('dancing baby...')
                        dance_baby(sense)
                    else:
                        pass
                else:
                    ## double clicks ##
                    if event.direction == 'up':
                        print('powering off...')
                        time.sleep(10)
                        subprocess.Popen(['shutdown','-h','now'])
                    elif event.direction == 'down':
                        pass
                    elif event.direction == 'left':
                        pass
                    elif event.direction == 'right':
                        print('toggling emails... setting to: %s ' % (not SEND_EMAILS))
                        SEND_EMAILS = not SEND_EMAILS
                    elif event.direction == 'middle':
                        print('getting random event...')
                        pass
                    else:
                        pass
            LAST = event.direction


def distribute_emails():
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
    sense.show_message("Temperature: %s .C  Humidity: %s percent  Pressure: %s mb" % (temp, humidity, pressure))
    return


def get_date(sense):
    local_time = time.ctime(time.time())
    sense.show_message("Date: %s " % (local_time))
    return

def dance_baby(sense):
    return

# if __name__ == "__main__":
#     t1 = Thread(target = watch_pi)
#     t2 = Thread(target = distribute_emails)
#     t1.setDaemon(True)
#     t2.setDaemon(True)
#     t1.start()
#     t2.start()
#     while True:
#         pass

