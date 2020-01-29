# Auto Light

Autoamtically adjusts the brightness level for all internal and external monitors based on solar irradience for your location.

Currently supported on Windows only.

 - Sun data is taken from pysolar module
 - External monitors are controlled using DDCI trough modified mccs module from https://github.com/ChristopherHammond13/ddc-windows/blob/master/mccs.py
 - Laptop monitor is controlled using wmi module

## Usage

At current state the app has no GUI, just a tray icon. So the settings can be changed only using config file.
At first run it will create the following json file:
json
``
{
    "brightness_min": 50,
    "brightness_max": 100,
    "latitude": 54.69,
    "longitude": 25.26
}
``

All you need to do is:
 - Put it in your coordinates (Good enough to have an acuracy of 100km or so) 
 - Enter desired min and max brightness thresholds
 - Save the file and restart the app.
 
After startup you can check the current status or exit the app by right clicking on the tray icon.

## Support

You can report bugs here, so that me or anyone else can fix them (code is simple).