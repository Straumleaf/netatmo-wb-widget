#!/usr/bin/env python3

import lnetatmo                                         # API package for Netatmo station
import json                                             # JSON package 
import sys
import types                                            # adding constants type
import datetime                                         # date and time
import time                                             # adding delay to app execution

from urllib import request, error                       # to check availability of Internet connection

# netatmo.com URL to test network availability
URL_TO_TEST = 'http://netatmo.com'

# color scheme for tooltip
BLUE = '#5A85DB'        #00BFFF
GREEN = '#A3BE8C'       #00FF7F
YELLOW = '#EBCB8B'      #FFFF00
RED = '#BF616A'         #FF4500
WHITE = '#FFFFFF'

# tooltip header text
TOOLTIP_HD = f"<span font='Euro Technic Extended 14'>                     Netatmo</span>"

# app error messages resource
ERROR_01_MSG = ' Server Error! '
ERROR_01_DESC = ' Error - Request to Netatmo Server were failed!\n or another unknown exception '
ERROR_02_MSG = ' Station Name - N/A '
ERROR_02_DESC = ' Please put Netatmo weather station name\n beside netatmo-wb-widget.pu in waybar config file '
ERROR_03_MSG = ' Connecting... '
ERROR_03_DESC = ' No Internet connection available. Times tried to connect - '
ERROR_04_MSG = ' No Internet! '
ERROR_04_DESC = ' No Internet connection available. '

# standard netatmo sensors resources
constants = types.SimpleNamespace()
constants.TEMP = 'Temperature'
constants.HUMID = 'Humidity'
constants.CO2 = 'CO2'
constants.PRES = 'Pressure'
constants.BAT = 'battery_percent'

# function just wrap value in css color tag
def wrap_in_color_tag(val, color = None):
    return f"<span color=\"{WHITE}\">{val}</span>" if color is None else f"<span color=\"{color}\">{val}</span>"

# return sensor alias if available
def sensor_alias(sensor):
    match sensor:
        case constants.BAT:
            return 'Battery'
        case _:
            return sensor

# generating ending/type for the given value 
def value_postfix(sensor):
    match sensor:
        case constants.TEMP:
            return '°C'
        case constants.CO2:
            return 'ppm'
        case constants.HUMID:
            return '%'
        case constants.BAT:
            return '%'
        case constants.PRES:
            return 'mbar'

# assigning color and place to the value in the string
def value_place_and_color(val, sensor):
    # default formating string placement
    val_str = '\t' + str(val)
    match sensor:
        case constants.TEMP:
            if val < 3:
                return wrap_in_color_tag(val_str, BLUE)
            if val < 15:
                return wrap_in_color_tag(val_str, GREEN)
            if val < 27:
                return wrap_in_color_tag(val_str, YELLOW)
            else:
                return wrap_in_color_tag(val_str, RED)
        case constants.CO2:
            val_str = '\t\t' + str(val)
            if val < 1000:
                return wrap_in_color_tag(val_str, GREEN)
            if val < 1500:
                return wrap_in_color_tag(val_str, YELLOW)
            else:
                return wrap_in_color_tag(val_str, RED)
        case constants.BAT:
            if val < 30:
                return wrap_in_color_tag(val_str, RED)
            if val < 60:
                return wrap_in_color_tag(val_str, YELLOW)
            else:
                return wrap_in_color_tag(val_str, GREEN)
        case constants.HUMID:
            if val < 40 or val > 60:
                return wrap_in_color_tag(val_str, RED)
            else:
                return wrap_in_color_tag(val_str, GREEN)
        case _:
            return wrap_in_color_tag(val_str)
    
# street environment status based on a temperature value
def temp_status(temp):
    if temp > 28:
        return 'hot'
    if temp < 3:
        return 'cold'
    else:
        return 'normal'

# initializing the list of weather station sensors
def list_of_sensors(numberOfModules):
    listOfSensors = [[]] * numberOfModules

    # initialization of standard modules (one indoor + one outdoor) 
    listOfSensors[0] = [constants.TEMP, constants.HUMID, constants.BAT]
    listOfSensors[-1] = [constants.TEMP, constants.HUMID, constants.CO2, constants.PRES]

    # initialization of additional modules
    i = 1
    if numberOfModules > 2:
        while i < (numberOfModules - 1):
            listOfSensors[i] = [constants.TEMP, constants.HUMID, constants.CO2, constants.BAT]
            i += 1

    return listOfSensors

# check network availability by opening 'netatmo.com' URL
def internet_ready():
    try:
        request.urlopen(URL_TO_TEST, timeout = 1)
        return True
    except error.URLError:
        return False

## MAIN --------------------------------------------------------------------------        

def main(args):
    # declaring dictionary for JSON output and list of station sensors
    plugin_msg = {}

    # authorizing as per credentials stored in '~/.netatmo.credentials' file
    authorization = lnetatmo.ClientAuth()

    # reading 1st argument to get Netatmo station name
    # and checking if not empty
    if len(args) < 2:
        plugin_msg['text'] = ERROR_02_MSG
        plugin_msg['tooltip'] = ERROR_02_DESC
    else:
        stationName = args[1]

        try:
            # geting station devices list and most recent telemetry
            stationData = lnetatmo.WeatherStationData(authorization)
            stationModulesList = stationData.modulesNamesList(stationName)      # for some reason it is not required to mention station name but  
            lastStationData = stationData.lastData()                            # instead you need to put just one space(20) symbol - ' ' or anything but not empty
            
            # loading available modules and sensors
            numberOfModules = len(stationModulesList)
            listOfSensors = list_of_sensors(numberOfModules)
        
            # creating the waybar widget text
            outdoorTemp = lastStationData[stationModulesList[0]][listOfSensors[0][0]]
            plugin_msg['text'] = f" {outdoorTemp}°C"

            # creating widget tooltip
            plugin_msg['tooltip'] = TOOLTIP_HD
            for station, sensorList in zip(stationModulesList, listOfSensors):
                plugin_msg['tooltip'] += f"\n<b>{station}:</b>\n"
                for sensor in sensorList:
                    plugin_msg['tooltip'] += f" {sensor_alias(sensor)} - {value_place_and_color(lastStationData[station][sensor], sensor)} {value_postfix(sensor)}\n"

            # insert a time stamp
            now = datetime.datetime.now()
            plugin_msg['tooltip'] += f"\n <span font='8'>{stationName}, updated: - {now.strftime('%H%Mhrs %d/%m')}</span>"
            # creating class type for waybar widget to use it in css file
            plugin_msg['class'] = f"{temp_status(outdoorTemp)}"

        except:
            # stub if something were going not right
            plugin_msg['text'] = ERROR_01_MSG if internet_ready() else ERROR_04_MSG
            plugin_msg['tooltip'] = ERROR_01_DESC if internet_ready() else ERROR_04_DESC

    # returning data to waybar widget in JSON format
    print(json.dumps(plugin_msg))

if __name__=='__main__':
  
    error_msg = {}
    connection_tries = 0

    # checking Internet and/or trying to connect 
    while not internet_ready() and connection_tries < 3:
        error_msg['text'] = ERROR_03_MSG
        error_msg['tooltip'] = ERROR_03_DESC + str(connection_tries)
        print(json.dumps(error_msg))
        connection_tries += 1

        # wait for 3 sec before the next try
        time.sleep(3)
  
    main(sys.argv)
