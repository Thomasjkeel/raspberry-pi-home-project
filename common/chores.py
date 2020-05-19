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
DAILY_CHORES = {
    "Walkies": ALL_PEOPLE,
    "Dishes": ALL_PEOPLE[[1, 2, 3, 0]],
    "Lunch": ALL_PEOPLE[[2, 3, 0, 2, 3, 0]],
    "Dinner": ALL_PEOPLE[[3, 0, 1, 2]],
    "Feed Animals": ALL_PEOPLE[[1, 3, 0, 2]],
    "Clean Room": ALL_PEOPLE[[2, 1, 3, 0]]
}

WEEKLY_CHORES = {
    "Hoovering": ALL_PEOPLE,
    "Bathrooms": ALL_PEOPLE[[1, 2, 3, 0]],
    "Kitchen": ALL_PEOPLE[[3,0,2,1]],
    "Bins": ALL_PEOPLE[[2, 1, 3, 0]],
    "Dusting": ALL_PEOPLE[[1, 3, 0, 2]],
    "Watering": ALL_PEOPLE[[3, 0, 1, 2]]
}
NUMBER_PEOPLE = len(ALL_PEOPLE)

CHORE_TXT = '/home/pi/Documents/home_chores_project/raspberry-pi-home-project/day_log.txt'


def read_and_update_day_counter():
    # load in data and check how many days ago the last one was and divide by 4
    with open(CHORE_TXT) as json_file:
        day_log = json.load(json_file)
        # order dates
        today = datetime.datetime.now()
        # order data by days from: https://stackoverflow.com/questions/34129391/sort-python-dictionary-by-date-key/34129758
        ordered_data = sorted(day_log.items(), key=lambda x: datetime.datetime.strptime(
            x[0], '%d %b %Y'), reverse=True)
        earliest = ordered_data[-1]
        
        difference = datetime.datetime.strptime(earliest[0], '%d %b %Y') - today
        days_away = int(difference.days)

        earliest_counter = earliest[1][0]
        # day counter (i.e current day number)
        day_counter = (days_away + earliest_counter)
        current_day_index = day_counter % NUMBER_PEOPLE

        # week counter (current week number)
        week_counter = earliest[1][1]
        date_counter_changes = False
        for val in ordered_data:
            if val[1][1] > week_counter:
                date_counter_changes = val[0]
                break
        if date_counter_changes:
            difference = datetime.datetime.strptime(date_counter_changes, '%d %b %Y') - today
            days_until_change = difference.days
            next_change = days_until_change % 7
        else:
            next_change = 7
        # preserve the week number and increase if past the threshold day
        for i in range(0, 7):
            if i >= next_change:
                week_counter += 1
            day_log[(today + datetime.timedelta(days=i)).strftime('%d %b %Y')
                    ] = [day_counter % NUMBER_PEOPLE, week_counter]
            day_counter += 1

        with open(CHORE_TXT, 'w') as outfile:
            json.dump(day_log, outfile)

    return current_day_index, day_log[today.strftime('%d %b %Y')][1]


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
    current_day_index, current_week = read_and_update_day_counter()
    today = datetime.datetime.now().strftime('%d %b')
    chore_message = 'Daily Chores  %s: ' % (today)

    daily_chores = {i: [] for i in ALL_PEOPLE}
    for dkey in DAILY_CHORES.keys():
        chore_message += dkey + ": " + DAILY_CHORES[dkey][current_day_index] + '  '
        daily_chores[DAILY_CHORES[dkey][current_day_index]].append(dkey)

    _, last_day = get_current_week_range()
    weekly_chores = {i: [] for i in ALL_PEOPLE}
    chore_message += 'Weekly Chores up to' + str(last_day)
    for wkey in WEEKLY_CHORES.keys():
        print(wkey, current_week)
        chore_message += wkey + ": " + \
            WEEKLY_CHORES[wkey][current_week] + '  '
        weekly_chores[WEEKLY_CHORES[wkey][current_week]].append(wkey)
    all_chores = {'daily': daily_chores, 'weekly': weekly_chores}

    return chore_message, all_chores
