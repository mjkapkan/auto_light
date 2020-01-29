# Auto display brightness proportional to sun power output for specific day.
# author: mjkapkan
import os
import mccs
import pystray
import json
import wmi
from threading import Thread
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
    
init_icon = Thread(target=run_icon)
init_icon.start()

monitor_conf = {}

def send_to_local(brigthness_int):
    print('Executing Command on monitor local')
    wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(brigthness_int, 0)

def change_brightness(value):
    send_to_local(value)            #changes laptop screen brightness
    mccs.send_to_all('10',value)    #changes external screen brightness through ddci

start_date = 'start'
current_brightness = 0
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
            new_brightness = day_data[time]['brightness']
            status = 'Using brightness ' + str(new_brightness) + ' for (UTC) ' + time + '. Sun position: ' + str(round(day_data[time]['position'],2)) + '° Sun power: ' + str(round(day_data[time]['power'],2)) + ' W'
            
        else:
            new_brightness = user_settings['brightness_min']
            status = 'After sunset or no sun data at ' + time + ', using minimum brightness: ' + str(new_brightness)
        if new_brightness != current_brightness:
            current_brightness = new_brightness
            print('Changing Brightness to: ' + str(current_brightness))
            change_brightness(current_brightness)
        main_icon.menu = update_icon_menu()
        main_icon.update_menu()
        dl(2)

init_icon.join()