"""
    Functions for determining whose chores it is today 
"""
import time
import json

# {'6':'Sunday','0':'Monday'}

time.localtime().tm_wday 

def get_chores(sense):
    # sense.show_message("Temperature: %s .C  Humidity: %s percent  Pressure: %s mb" % (temp, humidity, pressure))
    print('these are the chores...')
    sense.show_message('Chores %s ' % (time.localtime().tm_wday))
    return