#!/usr/bin/python3.6

# Скрипт для реализации функционала "светового будильника" Xiaomi Philips Zhirui Bedside Lamp
# Предполагается периодический запуск данного скрипта планировщиком (например, cron)
# Version 0.3. By iw0rm3r, 2020. https://github.com/iw0rm3r

# Настройки
MAX_BRIGHTNESS = 46
MIN_BRIGHTNESS = 1
MAX_COLOR_TEMP = 23
MIN_COLOR_TEMP = 1
EXPONENTIAL_LIKE_PROGRESSION = True

import configparser, os
from miio import PhilipsMoonlight
from datetime import date, datetime, timedelta

def writeSkipTimeToConfig():
    config['Alarm settings']['Skip alarm time'] = alarm_time.strftime("%d.%m.%Y %H:%M")
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def calculateValues(min_value, max_value):
    value = ( (minutes_after_start * (max_value - min_value)) / minutes_before_alarm ) + min_value
    if EXPONENTIAL_LIKE_PROGRESSION:
        # print('Raw value is: {}' .format(value))
        value = (1 / max_value)**2 * value**3
        if value < min_value:
            value = min_value
    return round(value)

config = configparser.ConfigParser()
script_dir = os.path.dirname(__file__)
config_path = os.path.join(script_dir, 'zhirui_settings.ini')
config.read(config_path)

print("Alarm script starting...")

# завершить исполнение скрипта, если будильник выключен
if config['Alarm settings']['Alarm enabled'] == 'false':
    print('Alarm is disabled, exiting...')
    quit()
    
print("Alarm is enabled, doing stuff...")

# проверка на вхождение в заданный временной промежуток
alarm_time_str = config['Alarm settings']['Alarm time']
minutes_before_alarm = int(config['Alarm settings']['Minutes before alarm'])
skip_alarm_datetime_str = config['Alarm settings']['Skip alarm time']
current_time = datetime.now()
alarm_time = datetime.combine(date.today(), datetime.strptime(alarm_time_str, '%H:%M').time())
alarm_datetime_str = alarm_time.strftime("%d.%m.%Y %H:%M")
alarm_start_time = alarm_time - timedelta(minutes = minutes_before_alarm)
alarm_finish_time = alarm_time + timedelta(minutes = 1)

print('Current time is: {}' .format(current_time))
print('Alarm time is: {}' .format(alarm_time))
print('Alarm start time is: {}' .format(alarm_start_time))

if current_time < alarm_start_time or current_time > alarm_finish_time:
    print('Too early, exiting...')
    quit()

if alarm_datetime_str == skip_alarm_datetime_str:
    print('This alarm has to be skipped, exiting...')
    quit()

# подготовка к управлению светильником
print('ALARM!!!')
minutes_after_start = int((current_time - alarm_start_time).seconds / 60)

IP = config['Device']['IP']
Token = config['Device']['Token']
zhirui = PhilipsMoonlight(IP, Token)

# если идёт первая минута пробуждения и светильник включён - значит будить не нужно, и следует сделать отметку о пропуске будильника на этот раз
if minutes_after_start < 1 and zhirui.status().is_on == True:
    print('Lamp is on already, skipping this alarm...')
    writeSkipTimeToConfig()
    quit()

# если идёт не первая минута пробуждения и светильник выключен - значит его выключили специально, и дальше будить смысла нет
if minutes_after_start >= 1 and zhirui.status().is_on == False:
    print('Lamp was turned off after alarm start, exiting...')
    writeSkipTimeToConfig()
    quit()

# обработка функции будильника
if minutes_after_start == 0:
    print('This is the first minute of alarm, enabling "night mode"...')
    zhirui.set_scene(6)
else:
    brightness = calculateValues(MIN_BRIGHTNESS, MAX_BRIGHTNESS)
    color_temp = calculateValues(MIN_COLOR_TEMP, MAX_COLOR_TEMP)

    print('Minutes after start: {}' .format(minutes_after_start))
    print('Current brightness is: {}' .format(brightness))
    print('Current color temp is: {}' .format(color_temp))

    zhirui.set_brightness_and_color_temperature(brightness, color_temp)
    print('Values were set.')