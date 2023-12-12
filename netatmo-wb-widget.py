#!/usr/bin/env python

import lnetatmo
import json

# weather station name
stationName = 'Homeworld'

# color scheme for widget tooltip
BLUE = '#5A85DB'        #00BFFF
GREEN = '#A3BE8C'       #00FF7F
YELLOW = '#EBCB8B'      #FFFF00
RED = '#BF616A'         #FF4500
WHITE = '#FFFFFF'

# function just wrap value in css color tag
def wrap_in_color_tag(val, color = None):
    if color is None:
        return f"<span color=\"{WHITE}\">{val}</span>"
    else:
        return f"<span color=\"{color}\">{val}</span>"

# return sensor alias if available
def sensor_alias(sensor):
    match sensor:
        case 'battery_percent':
            return 'Battery'
        case _:
            return sensor

# generating ending/type for the given value 
def value_postfix(sensor):
    match sensor:
        case 'Temperature':
            return '°C'
        case 'CO2':
            return 'ppm'
        case 'Humidity':
            return '%'
        case 'battery_percent':
            return '%'
        case 'Pressure':
            return 'mbar'

# assigning color and place to the value in the string
def value_place_and_color(val, sensor):
    match sensor:
        case 'Temperature':
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
        case 'CO2':
            if val < 500:
                val = '\t\t' + str(val)
                return wrap_in_color_tag(val, GREEN)
            if val < 1500:
                val = '\t\t' + str(val)
                return wrap_in_color_tag(val, YELLOW)
            else:
                val = '\t\t' + str(val)
                return wrap_in_color_tag(val, RED)
        case 'battery_percent':
            if val < 30:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, RED)
            if val < 60:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, YELLOW)
            else:
                val = '\t' + str(val)
                return wrap_in_color_tag(val, GREEN)
        case 'Humidity':
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
    listOfSensors[0] = ['Temperature', 'battery_percent']
    listOfSensors[-1] = ['Temperature', 'Humidity', 'CO2', 'Pressure']

    # initialization of additional modules
    i=1
    if numberOfModules > 2:
        while i < (numberOfModules - 1):
            listOfSensors[i] = ['Temperature', 'Humidity', 'CO2', 'battery_percent']
            i += 1

    return listOfSensors

# declaring dictionary for JSON output and list of station sensors
data = {}
listOfSensors = [[]]

# authorizing as per credentials stored in '~/.netatmo.credentials' file
authorization = lnetatmo.ClientAuth()

try:
    # geting station devices list and most recent telemetry
    stationData = lnetatmo.WeatherStationData(authorization)
    stationModulesList = stationData.modulesNamesList(stationName)
    lastStationData = stationData.lastData()
    
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
    data['text'] = f"Data - N/A"
    data['tooltip'] = f" Error - Netatmo Server request failed!\n or another unknown exception "

# returning data for waybar widget in JSON format
print(json.dumps(data))