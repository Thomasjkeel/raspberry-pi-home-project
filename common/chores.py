"""
    Description
    ================
    Functions for determining whose chores it is today. Uses a seperate file (day_log.txt) to keep itself in sync with the rota. 
"""

import datetime
import time
import numpy
import json

ALL_PEOPLE = numpy.array(['T', 'J', 'M', 'F'])
DAY_COUNTER = 0
WEEKLY_COUNTER = 0
DAILY_CHORES = {
    "Walkies": ALL_PEOPLE,
    "Dishes": ALL_PEOPLE[[1, 2, 3, 0]],
    "Lunch": ALL_PEOPLE[[2, 3, 0, 2, 3, 0]],
    "Dinner": ALL_PEOPLE[[3, 0, 1, 2]],
    "Feed Animals": ALL_PEOPLE[[1, 3, 0, 2]],
    "Clean Room": ALL_PEOPLE[[2, 1, 3, 0]]
}

WEEKLY_CHORES = {
    "Hoovering": ALL_PEOPLE[(WEEKLY_COUNTER+1) % 4],
    "Bathrooms": ALL_PEOPLE[(WEEKLY_COUNTER+2) % 4],
    "Kitchen": ALL_PEOPLE[(WEEKLY_COUNTER+3) % 4],
    "Bins": ALL_PEOPLE[WEEKLY_COUNTER % 4],
    "Dusting": ALL_PEOPLE[(WEEKLY_COUNTER+3) % 4],
    "Watering": ALL_PEOPLE[WEEKLY_COUNTER % 4]
}
NUMBER_PEOPLE = len(ALL_PEOPLE)

CHORE_TXT = '/home/pi/Documents/home_chores_project/raspberry-pi-home-project/day_log.txt'


def read_and_update_day_counter():
    global DAY_COUNTER, WEEKLY_COUNTER
    # load in data and check how many days ago the last one was and divide by 4
    with open(CHORE_TXT) as json_file:
        day_log = json.load(json_file)
    if save_log_file_status():
        # read last day and counter value
        all_days = list(day_log.keys())
        today = datetime.datetime.now()
        # determine how many days away the nearest date is:
        min_days_away = 999
        max_days_away = 0
        min_date = ''
        max_date = ''
        for day in all_days:
            difference = today - datetime.datetime.strptime(day, '%d %b %Y')
            days_away = difference.days
            if days_away <= min_days_away:
                min_date = day
            elif days_away >= max_days_away:
                max_date = day

        print(min_date, max_date)

        latest_week_counter = numpy.array(list(day_log.values()))[:, 1].max()
        
        difference = today - datetime.datetime.strptime(a_day[0], '%d %b %Y')
        # set WEEKLY_COUNTER
        days_away = difference.days
        counter_on_a_day = day[1][0]
        day_counter = (days_away + counter_on_a_day)
        week_counter = 0
    
        WEEKLY_COUNTER = latest_week_counter
        day_log = {}
        DAY_COUNTER = day_counter % NUMBER_PEOPLE
        for i in range(0, 7):
            if week_counter % 7 == 0:
                WEEKLY_COUNTER += 1
            day_log[(today + datetime.timedelta(days=i)).strftime('%d %b %Y')
                    ] = [day_counter % NUMBER_PEOPLE, WEEKLY_COUNTER]
            day_counter += 1
            week_counter += 1
    
    
        with open(CHORE_TXT, 'w') as outfile:
            json.dump(day_log, outfile)

    return DAY_COUNTER, day_log[today.strftime('%d %b %Y')][1]

def save_log_file_status():
    with open('save_log.txt') as my_file:
        save_day_log = my_file.read()
    
    if save_day_log == 'True':
        with open('save_log.txt', 'w') as my_file:
            my_file.write('False')
        return True
    else:
        return False


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
    global DAY_COUNTER
    DAY_COUNTER, current_week = read_and_update_day_counter()
    today = datetime.datetime.now().strftime('%d %b')
    chore_message = 'Daily Chores  %s: ' % (today)

    daily_chores = {i: [] for i in ALL_PEOPLE}
    for dkey in DAILY_CHORES.keys():
        chore_message += dkey + ": " + DAILY_CHORES[dkey][DAY_COUNTER] + '  '
        daily_chores[DAILY_CHORES[dkey][DAY_COUNTER]].append(dkey)

    _, last_day = get_current_week_range()
    weekly_chores = {i: [] for i in ALL_PEOPLE}
    chore_message += 'Weekly Chores up to' + str(last_day)
    for wkey in WEEKLY_CHORES.keys():
        print(current_week)
        print(WEEKLY_CHORES[wkey])
        print(WEEKLY_CHORES[wkey][current_week % 4])
        chore_message += wkey + ": " + \
            WEEKLY_CHORES[wkey][current_week % 4] + '  '
        weekly_chores[WEEKLY_CHORES[wkey][current_week % 4]].append(wkey)
    all_chores = {'daily': daily_chores, 'weekly': weekly_chores}

    return chore_message, all_chores
