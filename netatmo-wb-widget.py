#!/usr/bin/env python

import lnetatmo
import json
import sys
import types

# color scheme for widget tooltip
BLUE = '#5A85DB'        #00BFFF
GREEN = '#A3BE8C'       #00FF7F
YELLOW = '#EBCB8B'      #FFFF00
RED = '#BF616A'         #FF4500
WHITE = '#FFFFFF'

# error messages resource
ERROR_01_MSG = ' Comm Error! '
ERROR_01_DESC = ' Error - Netatmo Server request failed!\n or another unknown exception '
ERROR_02_MSG = ' Station Name - N/A '
ERROR_02_DESC = ' Please put Netatmo weather station name\n beside netatmo-wb-widget.pu in waybar config file '

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
    match sensor:
        case constants.TEMP:
            if val < 3:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, BLUE)
            if val < 15:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, GREEN)
            if val < 27:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, YELLOW)
            else:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, RED)
        case constants.CO2:
            if val < 500:
                val = '\t\t' + str(val)
                return wrap_in_color_tag(val, GREEN)
            if val < 1500:
                val = '\t\t' + str(val)
                return wrap_in_color_tag(val, YELLOW)
            else:
                val = '\t\t' + str(val)
                return wrap_in_color_tag(val, RED)
        case constants.BAT:
            if val < 30:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, RED)
            if val < 60:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, YELLOW)
            else:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, GREEN)
        case constants.HUMID:
            if val < 40 or val > 60:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, RED)
            else:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, GREEN)
        case _:
            val = '\t' + str(val)
            return wrap_in_color_tag(val)
    
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
    listOfSensors[0] = [constants.TEMP, constants.BAT]
    listOfSensors[-1] = [constants.TEMP, constants.HUMID, constants.CO2, constants.PRES]

    # initialization of additional modules
    i=1
    if numberOfModules > 2:
        while i < (numberOfModules - 1):
            listOfSensors[i] = [constants.TEMP, constants.HUMID, constants.CO2, constants.BAT]
            i += 1

    return listOfSensors

# declaring dictionary for JSON output and list of station sensors
data = {}

# authorizing as per credentials stored in '~/.netatmo.credentials' file
authorization = lnetatmo.ClientAuth()

# reading 1st argument to get Netatmo station name
# and checking if not empty
if len(sys.argv) < 2:
    data['text'] = ERROR_02_MSG
    data['tooltip'] = ERROR_02_DESC
else:
    stationName = sys.argv[1]

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
        data['text'] = f" {outdoorTemp}°C"

        # creating widget tooltip
        data['tooltip'] = f""
        for station, sensorList in zip(stationModulesList, listOfSensors):
            data['tooltip'] += f"\n<b>{station}:</b>\n"
            for sensor in sensorList:
                data['tooltip'] += f" {sensor_alias(sensor)} - {value_place_and_color(lastStationData[station][sensor], sensor)} {value_postfix(sensor)}\n"

        # creating class type for waybar widget to use it in css file
        data['class'] = f"{temp_status(outdoorTemp)}"

    except:
        # stub if something going not right
        data['text'] = ERROR_01_MSG 
        data['tooltip'] = ERROR_01_DESC

# returning data for waybar widget in JSON format
print(json.dumps(data))