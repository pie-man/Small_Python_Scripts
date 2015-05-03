#!/usr/bin/env python

import sys
import time
from w1thermsensor import W1ThermSensor
# To get w1thermsensor :
# git clone https://github.com/timofurrer/w1thermsensor.git && cd w1thermsensor
# sudo python setup.py install

locations = {
  "000005eb8b82" : "Pi",
  "0000062ac658" : "Wall",
  "0000062caad9" : "Window",
  "000005e9b365" : "ReadyNAS",
}

stats_periods = ("hourly","daily","weekly","monthly","yearly")

class Time_Period:
    '''defines time periods to calcualte stats over'''
    def __init__(self,name,modulo,divisor):
        self.name = name
        self.modulo = modulo
        self.divisor = divisor


countstep = 1

if len(sys.argv) > 1:
    reading_count = sys.argv[1]
    if reading_count.isdigit():
        reading_count = int(reading_count)
        if reading_count == 0:
            countstep = 0
            reading_count = 1
    else:
        reading_count = 1
else:
    reading_count = 1

timestamp = time.strftime("%Y%m%d-%H%M")

logfile= timestamp + r"-logfile.txt"
output = open(logfile,"w")

all_sensors = W1ThermSensor.get_available_sensors()

def match_sensor_to_loc(sensor):
    if sensor.id in locations:
        sensor_name = locations[sensor.id]
    else:
        sensor_name = "unk : "  + str(sensor.id)
    sensor.location = sensor_name
    return sensor_name

def init_sensor_stats(sensor):
    request_time = time.time()
    for period in stats_periods:
        period_value = get_period_values(request_time,period)
        reset_sensor_stats(sensor,period,period_value)

def reset_sensor_stats(sensor,period,new_period_value):
    sensor.max_temp[period] = 0.0
    sensor.min_temp[period] = 100.0
    sensor.avg_temp[period] = 0.0
    sensor.record_count[period] = 0
    sensor.last_reading[period] = new_period_value

def get_sensor_max(sensor,period,current_temp):
    sensor.max_temp[period] = max(sensor.max_temp[period],current_temp)

def get_sensor_min(sensor,period,current_temp):
    sensor.min_temp[period] = min(sensor.min_temp[period],current_temp)

def get_sensor_avg(sensor,period,current_temp):
    sensor.avg_temp[period] = ((sensor.avg_temp[period] * sensor.record_count[period]) + current_temp) \
                              / ( sensor.record_count[period] +1 )
    sensor.record_count[period] += 1

def get_all_temps():
    for sensor in all_sensors:
        sensor.last_temp = sensor.get_temperature()
#        sensor_name = sensor.location
        for period in stats_periods:
            get_sensor_max(sensor,period,sensor.last_temp)
            get_sensor_min(sensor,period,sensor.last_temp)
            get_sensor_avg(sensor,period,sensor.last_temp)

def get_period_values(timestamp,period):
    current_time = time.gmtime(timestamp)
    current = {}
    current["hourly"]  = current_time[3]
    current["daily"]   = current_time[7]
    current["weekly"]  = current_time[7] / 7
    current["monthly"] = current_time[1]
    current["yearly"]  = current_time[0]
    return current[period]

for sensor in all_sensors:
    match_sensor_to_loc(sensor)
    sensor.max_temp      = {}
    sensor.min_temp      = {}
    sensor.avg_temp      = {}
    sensor.record_count  = {}
    sensor.last_reading  = {}
    init_sensor_stats(sensor)
    output.write("%-23s |" % sensor.location)

output.write("\n")
 
for sensor in all_sensors:
    output.write("%5s %5s %5s %5s |" % ("curr","max","min","avg"))

output.write("\n")

#for i in range(121):
i = 0
while i < reading_count: 
    i = i + countstep
    request_time = time.time()
    get_all_temps()
    
    print "====== reading " + str(i) + " of " + str(reading_count) + " readings. ==== step is : " + str(countstep) + " ============="
    format_str = "current %4.1f    " + \
                 "max: %4.1f    " + \
                 "min: %4.1f    " + \
                 "avg: %4.1f    " + \
                 "readings: %5d   "
    for sensor in all_sensors:
        print ("%20s : " % sensor.location),
        for period in ("hourly","daily"):
            print ( format_str % (sensor.last_temp,
                                  sensor.max_temp[period],
                                  sensor.min_temp[period],
                                  sensor.avg_temp[period],
                                  sensor.record_count[period]
                           )) ,
        print ""
        output.write ("%5.1f %5.1f %5.1f %5.1f |" % 
                       (sensor.last_temp,
                        sensor.max_temp["daily"],
                        sensor.min_temp["daily"],
                        sensor.avg_temp["daily"]
                       ))
        for period in stats_periods:
            period_value = get_period_values(request_time,period)
            if period_value != sensor.last_reading[period]:
                reset_sensor_stats(sensor,period,period_value)
    output.write("\n")
    output.flush()
    print "======================================="
    if not i == reading_count:
      time.sleep(60)

output.close()
