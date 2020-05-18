"""
    Functions for determining whose chores it is today 
"""

import datetime 
import time
import numpy
import json

# {'6':'Sunday','0':'Monday'}

datetime.datetime.now().weekday 

ALL_PEOPLE = numpy.array(['Tom', 'Jonathan', 'Mum', 'Freya'])
DAY_COUNTER = 0
WEEKLY_COUNTER = 0
DAILY_CHORES = {
    "Walkies": ALL_PEOPLE,
    "Dishwasher": ALL_PEOPLE[[1, 2, 3, 0]],
    "Lunch": ALL_PEOPLE[[2, 3, 0, 1]],
    "Dinner": ALL_PEOPLE[[3, 0, 1, 2]],
    "Water Plants": ALL_PEOPLE[[0, 1, 2, 3]],
    "Feed Animals": ALL_PEOPLE[[1, 3, 0, 2]],
    "Clean Room": ALL_PEOPLE[[2, 1, 3, 0]]
}

WEEKLY_CHORES = {
    "Hoover": ALL_PEOPLE[(WEEKLY_COUNTER+1) % 4],
    "Clean Bathrooms": ALL_PEOPLE[(WEEKLY_COUNTER+2) % 4],
    "Clean Kitchen Sides": ALL_PEOPLE[(WEEKLY_COUNTER+3) % 4],
    "Recycling & Bins": ALL_PEOPLE[WEEKLY_COUNTER % 4]
}
NUMBER_PEOPLE = len(ALL_PEOPLE)

def read_and_update_day_counter():
    global DAY_COUNTER, WEEKLY_COUNTER
    # load in data and check how many days ago the last one was and divide by 4
    with open('day_log.txt') as json_file:
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
        day_log[(today + datetime.timedelta(days=i)).strftime('%d %b %Y')] = [day_counter % NUMBER_PEOPLE, WEEKLY_COUNTER]
        day_counter += 1
        week_counter += 1
        
    # re-save the file
    with open('day_log.txt', 'w') as outfile:
        json.dump(day_log, outfile)
    
    return DAY_COUNTER, day_log[today.strftime('%d %b %Y')][1]

def get_chores():
    global DAY_COUNTER, WEEKLY_COUNTER
    print('these are the chores...')
    DAY_COUNTER, WEEKLY_COUNTER = read_and_update_day_counter()
    today = datetime.datetime.now().strftime('%d %b %Y')
    chore_message = 'Chores on  %s: ' % (today)
    for dkey in DAILY_CHORES.keys():
        print(dkey)
        print(DAILY_CHORES[dkey] + ":" +  DAILY_CHORES[dkey][DAY_COUNTER] + '   ')
        chore_message.join(DAILY_CHORES[dkey] + ":" +  DAILY_CHORES[dkey][DAY_COUNTER] + '   ')

    for wkey in WEEKLY_CHORES.keys():
        chore_message.join(WEEKLY_CHORES[wkey] + ":" + WEEKLY_CHORES[wkey][WEEKLY_COUNTER] + '   ')

    return chore_message
