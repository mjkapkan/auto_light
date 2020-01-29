# Auto display brightness proportional to sun power output for specific day.
# author: mjkapkan
import os
import mccs
import wmi
import pytz
import pystray
import threading
import json
from subprocess import Popen
from sun_track import set_brigthtness_limits, get_day_data
from datetime import datetime as dt
from datetime import timedelta as dlt
from time import sleep as dl
from PIL import Image

app_name = 'Auto Light'
app_version = 1.1
app_title = app_name + ' ' + str(app_version)
path = os.path.realpath('') + '\\'
user_setting_file = path + 'auto_light_settings.json'
user_settings = {
    'brightness_min': 50,
    'brightness_max': 100,
    'latitude': 54.69,
    'longitude': 25.26
}
try:
    with open(user_setting_file,"r") as settings:
        user_settings = json.load(settings)
except FileNotFoundError:
    with open(user_setting_file,"w") as settings:
        json.dump(user_settings,settings,indent=4)

def close_icon(main_icon, item):
        global exit_app
        exit_app = not item.checked
        main_icon.stop()
def do_nothing():
    return

exit_app = False
status = ''
main_icon = None
def update_icon_menu():
    main_menu = pystray.Menu(
            pystray.MenuItem(
                app_title,None,enabled=False),
            pystray.MenuItem(
                'Status',
                pystray.Menu(
                    pystray.MenuItem(
                        status,do_nothing)
                )
            ),
            pystray.MenuItem(
                'Exit',
                close_icon,
                checked=lambda item: exit_app))
    return main_menu

main_menu = update_icon_menu()

def run_icon():
    global app_name
    global main_icon
    global main_menu
    global status
    main_icon = pystray.Icon(app_name)
    main_icon.icon = Image.open(path + "trayicon.ico")
    main_icon.menu = main_menu
    
    main_icon.run()
    
init_icon = threading.Thread(target=run_icon)
init_icon.start()

monitor_conf = {}





## OLD METHOD (Required external app support)
# for file in os.listdir(path):
#     fl = file.split('.')
#     if len(fl) > 1:
#         if fl[1] == 'cfg' and fl[0] != 'ControlMyMonitor':
#             with open(file, 'r') as cf:
#                 monitor_conf[fl[0]] = {}
#                 for line in cf:
#                     conf = line.strip().split('=')
#                     if len(conf) > 1:
#                         monitor_conf[fl[0]][conf[0]] = conf[1]

# cmd = path + 'ControlMyMonitor.exe /SetValue'

# def change_brightness(value):
#     for monitor in monitor_conf:
#         setting = '10'
#         value = str(value)
#         display = monitor_conf[monitor]['MonitorDeviceName']
#         chg_cmd = ' '.join([cmd,'"' + display + '"',setting,value])
#         Popen(chg_cmd).communicate()

def change_brightness(value):
    wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(value, 0) #changes laptop screen brightness
    mccs.send_to_all('10',value)                                                         #changes external screen brightness through ddci

start_date = 'start'
new_brightness = 0
while True:
    if exit_app:
        break
    else:
        if dt.now().strftime("%Y-%m-%d") != start_date:
            print('Gettin sun data...')
            day_data = set_brigthtness_limits(
                get_day_data(
                    user_settings['latitude'],user_settings['longitude']
                ),
                user_settings['brightness_min'],
                user_settings['brightness_max']
            )
            start_date = dt.now().strftime("%Y-%m-%d")
        time = dt.utcnow().strftime("%H:%M")
        if time in day_data:
            if day_data[time]['brightness'] != new_brightness:
                new_brightness = day_data[time]['brightness']
                print('Changing Brightness to: ' + str(new_brightness))
                change_brightness(new_brightness)
            status = 'Using brightness ' + str(new_brightness) + ' for (UTC) ' + time + '. Sun position: ' + str(round(day_data[time]['position'],2)) + '° Sun power: ' + str(round(day_data[time]['power'],2)) + ' W'
            
        else:
            status = 'After sunset or no sun data at ' + time + ', using minimum brightness: ' + str(user_settings['brightness_min'])
            change_brightness(user_settings['brightness_min'])
        main_icon.menu = update_icon_menu()
        main_icon.update_menu()
        dl(2)

init_icon.join()