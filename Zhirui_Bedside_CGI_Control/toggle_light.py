#!/usr/bin/python3.6

# Скрипт для переключения состояния светильника Xiaomi Philips Zhirui Bedside Lamp
# Version 0.1. By iw0rm3r, 2020. https://github.com/iw0rm3r

import configparser
from miio import PhilipsMoonlight

config = configparser.ConfigParser()
config.read('zhirui_settings.ini')
IP = config['Device']['IP']
Token = config['Device']['Token']

print("Content-type: text/html\n") # the mime-type header

print('<link rel="icon" type="image/png" sizes="16x16" href="./lightbulb-16x16.png">')
print('<link rel="apple-touch-icon" type="image/png" sizes="180x180" href="./lightbulb-apple-180x180.png">')

print("Detecting lamp state...<br>")

zhirui = PhilipsMoonlight(IP, Token)

if zhirui.status().is_on == True:
    print("Lamp if on, turning off...<br>")
    zhirui.off()
else:
    print("Lamp if off, turning on...<br>")
    zhirui.on()
