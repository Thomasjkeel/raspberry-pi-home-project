"""
    Functions for determining whose chores it is today 
"""

import datetime
import time
import numpy
import json


datetime.datetime.now().weekday

ALL_PEOPLE = numpy.array(['T', 'J', 'M', 'F'])
DAY_COUNTER = 0
WEEKLY_COUNTER = 0
DAILY_CHORES = {
    "Walkies": ALL_PEOPLE,
    "Dishes": ALL_PEOPLE[[1, 2, 3, 0]],
    "Lunch": ALL_PEOPLE[[2, 3, 0, 1]],
    "Dinner": ALL_PEOPLE[[3, 0, 1, 2]],
    "Watering": ALL_PEOPLE[[0, 1, 2, 3]],
    "Animals": ALL_PEOPLE[[1, 3, 0, 2]],
    "Clean Room": ALL_PEOPLE[[2, 1, 3, 0]]
}

WEEKLY_CHORES = {
    "Hoover": ALL_PEOPLE[(WEEKLY_COUNTER+1) % 4],
    "Bathrooms": ALL_PEOPLE[(WEEKLY_COUNTER+2) % 4],
    "Kitchen": ALL_PEOPLE[(WEEKLY_COUNTER+3) % 4],
    "Bins": ALL_PEOPLE[WEEKLY_COUNTER % 4]
}
NUMBER_PEOPLE = len(ALL_PEOPLE)

CHORE_TXT = '/home/pi/Documents/home_chores_project/raspberry-pi-home-project/day_log.txt'


def read_and_update_day_counter():
    global DAY_COUNTER, WEEKLY_COUNTER
    # load in data and check how many days ago the last one was and divide by 4
    with open(CHORE_TXT) as json_file:
        day_log = json.load(json_file)
    # read last day and counter value
    last_day, current_counters = day_log.popitem()
    # then how many days away:
    today = datetime.datetime.now()
    difference = today - datetime.datetime.strptime(last_day, '%d %b %Y')
    days_away = difference.days
    day_counter = (days_away + current_counters[0])
    week_counter = current_counters[1]
    day_log = {}
    DAY_COUNTER = day_counter % NUMBER_PEOPLE
    for i in range(0, 7):
        if week_counter % 7 == 0:
            WEEKLY_COUNTER += 1
        day_log[(today + datetime.timedelta(days=i)).strftime('%d %b %Y')
                ] = [day_counter % NUMBER_PEOPLE, WEEKLY_COUNTER]
        day_counter += 1
        week_counter += 1

    # re-save the file
    with open(CHORE_TXT, 'w') as outfile:
        json.dump(day_log, outfile)

    return DAY_COUNTER, day_log[today.strftime('%d %b %Y')][1]


def get_current_week_range():
    with open(CHORE_TXT) as json_file:
        day_log = json.load(json_file)

    current_day = list(day_log.keys())[0]
    current_week_counter = day_log[current_day][1]
    last_day = ''
    for wkey in day_log.keys():
        if day_log[wkey][1] > current_week_counter:
            last_day = wkey
            break
    return current_day, last_day


def get_chores():
    global DAY_COUNTER, WEEKLY_COUNTER
    DAY_COUNTER, WEEKLY_COUNTER = read_and_update_day_counter()
    today = datetime.datetime.now().strftime('%d %b')
    chore_message = 'Daily Chores  %s: ' % (today)

    daily_chores = {i: [] for i in ALL_PEOPLE}
    for dkey in DAILY_CHORES.keys():
        chore_message += dkey + ": " + DAILY_CHORES[dkey][DAY_COUNTER] + '  '
        daily_chores[DAILY_CHORES[dkey][DAY_COUNTER]].append(dkey)

    current_day, last_day = get_current_week_range()
    weekly_chores = {i: [] for i in ALL_PEOPLE}
    chore_message += 'Weekly Chores up to %s ' % (str(last_day))
    for wkey in WEEKLY_CHORES.keys():
        chore_message += wkey + ": " + \
            WEEKLY_CHORES[wkey][WEEKLY_COUNTER % 4] + '  '
        weekly_chores[WEEKLY_CHORES[wkey][WEEKLY_COUNTER % 4]].append(wkey)
    all_chores = {'daily': daily_chores, 'weekly': weekly_chores}

    return chore_message, all_chores
