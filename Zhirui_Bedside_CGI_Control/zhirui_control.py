#!/usr/bin/python3.6

# Скрипт для управления светильником Xiaomi Philips Zhirui Bedside Lamp
# Version 0.1. By iw0rm3r, 2020. https://github.com/iw0rm3r

import cgi, cgitb # modules for CGI handling
from miio import PhilipsMoonlight
import re # регулярные выражения
import configparser

settings_file_name = 'zhirui_settings.ini'

arguments = cgi.FieldStorage() # хранилище аргументов, полученных из среды

config = configparser.ConfigParser()
config.read(settings_file_name)
IP = config['Device']['IP']
token = config['Device']['Token']

zhirui = PhilipsMoonlight(IP, token)
zhirui_status = zhirui.status()

power = zhirui.status().is_on
brightness = 0
color_temp = 0
color = [0, 0, 0]
alarm_enabled_check = ''

print('Content-type: text/html\n') # the mime-type header
print("""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Zhirui control</title>
    <link rel="icon" type="image/png" sizes="16x16" href="./lightbulb-16x16.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="./lightbulb-apple-180x180.png">
    <style type="text/css">
    div.content {
        width: 300px;
        margin:0 auto;
    }
    body {
        background-color: #2f3031;
        color: #e5e4e2;
        font-family: system-ui;
        font-size: 16px;
    }
    label {
        float: left;
        clear: both;
    }
    input {
        font-size: inherit;
    }
    input[type="range"] {
        float: right;
    }
    input[type="text"] {
        width: 100px;
        float: right;
    }
    input[type="submit"] {
    }
    button {
        font-size: inherit;
    }
    </style>
</head>
<body>
<script src="jscolor.js"></script>
<div class="content">

<h1 align="center">Zhirui control</h1>
""")

# Проверяем наличие определённых параметров, их корректность, и задаём их
bright_temp_recieved = False
if 'brightness' in arguments and 'color_temp' in arguments:
    brightness = int(arguments.getvalue('brightness'))
    color_temp = int(arguments.getvalue('color_temp'))
    if brightness > 0 and brightness <= 100 and \
       color_temp > 0 and color_temp <= 100:
        # print('<p align="justify">Setting brightness and color temperature parameters...</p>')
        bright_temp_recieved = True
        zhirui.set_brightness_and_color_temperature(brightness, color_temp)

color_bright_recieved = False
if 'rgb_brightness' in arguments: # цвет и яркость
    # вынимаем список значений из RGBA строки
    rgba_strings = re.findall(r'\d+(?:\.\d+)?', arguments.getvalue('rgb_brightness'))
    # конвертируем список string в список int, проверяем корректность
    color_in_range = True
    color_not_null = False
    for i in range(0, 3): 
        color[i] = int(rgba_strings[i])
        if color[i] < 0 or color[i] > 255:
            color_in_range = False
        if color[i] != 0:
            color_not_null = True
    # конвертируем яркость из доли в проценты
    brightness = int(float(rgba_strings[3]) * 100)
    if brightness > 0 and brightness <= 100 and color_in_range == True \
       and color_not_null == True:
        # print('<p align="justify">Setting color and brightness parameters...</p>')
        color_bright_recieved = True
        zhirui.set_brightness_and_rgb(brightness, tuple(color[0:3]))

if 'night_mode' in arguments and arguments.getvalue('night_mode') == 'true':
    # print('<p align="justify">Entering night mode...</p>')
    zhirui.set_scene(6)

if 'toggle_light' in arguments and arguments.getvalue('toggle_light') == 'true':
    # print('<p align="justify">Switching the light...</p>')
    if power == True:
        zhirui.off()
        power = False;
    else:
        zhirui.on()
        power = True;

if 'alarm_time' in arguments and 'minutes_before_alarm' in arguments:
    if 'alarm_enabled' in arguments and arguments.getvalue('alarm_enabled') == 'on':
        alarm_enabled = 'true'
        alarm_enabled_check = 'checked'
    else:
        alarm_enabled = 'false'
    alarm_time = arguments.getvalue('alarm_time')
    minutes_before_alarm = arguments.getvalue('minutes_before_alarm')
    
    config['Alarm settings']['Alarm enabled'] = alarm_enabled
    config['Alarm settings']['Alarm time'] = alarm_time
    config['Alarm settings']['Minutes before alarm'] = minutes_before_alarm
    
    with open(settings_file_name, 'w') as configfile:
        config.write(configfile)
else:
    if config['Alarm settings']['Alarm enabled'] == 'true':
        alarm_enabled_check = 'checked'
    alarm_time = config['Alarm settings']['Alarm time']
    minutes_before_alarm = config['Alarm settings']['Minutes before alarm']


# Получаем из самого устройтсва те значения, которые не были переданы из среды
if bright_temp_recieved == False:
    # print('<p align="justify">No valid brightness and color temperature were recieved!</p>\n')
    color_temp = zhirui_status.color_temperature
if color_bright_recieved == False:
    # print('<p align="justify">No valid color and brightness were recieved!</p>\n')
    retrieved_color = zhirui_status.rgb
    for i in range(0, 3): 
        color[i] = int(retrieved_color[i])
if bright_temp_recieved == False and color_bright_recieved == False:
    # print('<p align="justify">Retrieving brightness...</p>\n')
    brightness = zhirui_status.brightness


# Генерируем формы ввода
print('<p><form action = "" method = "post">')
print('Light is on: {}<br>' .format(power))
print('<button name="toggle_light" value = "true">Toggle</button>')
print('</form><p>\n')

print('<p><form action = "" method = "post">')
print('<label>Brightness:</label><input type="range" min="1" max="100" step="1" name = "brightness" value="{}"><br>' .format(brightness))
print('<label>Color temperature:</label><input type="range" min="1" max="100" step="1" name = "color_temp" value="{}"><br>' .format(color_temp))
print('<input type = "submit" value = "Apply">\n</form></p>\n')

print("""<p><form action = "" method = "post">
<label>Color:</label><button data-jscolor="{valueElement:'#val4', alphaElement:'#alp4'}"></button><br>""")
print('<label>Value:</label><input name = "rgb_brightness" id="val4" value="rgba({},{},{},{})"><br>' .format(color[0], color[1], color[2], brightness / 100))
print('<input type = "submit" value = "Apply">\n</form></p>\n')

print("""<p><form action = "" method = "post">
<button name="night_mode" value = "true">Enter night mode...</button>
</form><p>\n""")

print('<p><center>Alarm settings:</center><form action = "" method = "post">')
print('<label>Enabled:</label><input type="checkbox" name = "alarm_enabled" {}><br>' .format(alarm_enabled_check))
print('<label>Alarm time:</label><input type="text" name = "alarm_time" value="{}"><br>' .format(alarm_time))
print('<label>Minutes before alarm:</label><input type="text" name = "minutes_before_alarm" value="{}"><br>' .format(minutes_before_alarm))
print('<input type = "submit" value = "Apply">\n</form></p>\n')

print("""</div>
</body>
</html>""")
