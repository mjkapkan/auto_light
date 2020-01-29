from pysolar.solar import *
import datetime, operator


def get_day_data(latitude,longitude):
    latitude_deg = latitude # positive in the northern hemisphere
    longitude_deg = longitude # negative reckoning west from prime meridian in Greenwich, England
    ##date = datetime.datetime(2018, 9, 26, 10, 11, 1, 130320, tzinfo=datetime.timezone.utc)


    date = datetime.datetime.utcnow()
    date = date.replace(tzinfo=datetime.timezone.utc)
    sod = date.replace(hour=0,minute=0,tzinfo=datetime.timezone.utc)
    eod = date.replace(hour=23,minute=58,tzinfo=datetime.timezone.utc)
    altitude_deg = get_altitude(latitude_deg, longitude_deg, date)

    minutes = 0
    date = sod
    day_data = {}
    while date < eod:
        minutes += 1
        date = sod + datetime.timedelta(minutes=minutes)
        altitude_deg = get_altitude(latitude_deg, longitude_deg, date)
        position = get_altitude(latitude_deg, longitude_deg, date)
        try:
            power = radiation.get_radiation_direct(date, altitude_deg)
        except OverflowError:
            continue
        if position > 1:
            time_frame = date.strftime("%H:%M")
            day_data[time_frame] = {}
            day_data[time_frame]['position'] = position
            day_data[time_frame]['power'] = power
    
    return day_data


def set_brigthtness_limits(day_data_dict,brightness_min,brightness_max):
    power_list = []
    for time_frame in day_data_dict:
        power_list.append(day_data_dict[time_frame]['power'])

    max_power = int(round(max(power_list),0))
    graduation = int(round((max_power / (brightness_max - brightness_min)),0))-1

    brightness = brightness_min
    gc = 0
    tc = 0

    power_mapping = {}
    for power in range(0,max_power+1):
        tc += 1
        gc += 1
        inc = 1
        if tc > max_power:
            inc = -1
        if gc == graduation:
            brightness += inc
            gc = 0
        if brightness < brightness_min:
            brightness = brightness_min
        elif brightness > brightness_max:
            brightness = brightness_max
        power_mapping[power] = brightness

    for time_frame in day_data_dict:           
        day_data_dict[time_frame]['brightness'] = power_mapping[int(round(day_data_dict[time_frame]['power'],0))]

    return day_data_dict

####Example:
##data = set_brigthtness_limits(get_day_data(54.699402,25.265306),30,100)
##
##for tf in data:
##    print(tf,data[tf])
