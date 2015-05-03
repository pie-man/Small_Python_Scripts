#!/usr/bin/env python

import sys
import time
from w1thermsensor import W1ThermSensor
# To get w1thermsensor :
# git clone https://github.com/timofurrer/w1thermsensor.git && cd w1thermsensor
# sudo python setup.py install

reading_interval = 60 # seconds between readings.

# Human readable names for the sensors indexed by unique sensor ID
locations = {
  "000005eb8b82" : "Window",
  "000005e9b365" : "Eaves",
  "0000062ac658" : "Wall",
  "0000062caad9" : "Printer",
  "000005ea107a" : "Pi",
}

class Time_Period:
    '''defines time periods to calcualte stats over'''
    def __init__(self,name,index,adjust_type=None,adjust_value=0):
        self.name=name
        self.index=index
        if adjust_type is not None:
            self.adjust_type  = adjust_type
            self.adjust_value = adjust_value
    def calc_value(self,cur_time):
        value = cur_time[self.index]
        if hasattr (self,"adjust_type"):
            if self.adjust_type == "divide":
                value = value / self.adjust_value
            elif self.adjust_type == "modulo":
                value = value % self.adjust_value
            elif self.adjust_type == ",multiply":
                value = value * self.adjust_value
            else:
                print "Unknown type of adjustment : " + self.adjust_type
        return value
    def get_period_values(self,timestamp):
        current_time = time.gmtime(timestamp)
        return self.calc_value(current_time)

stats_periods = {
        "hourly"   : Time_Period("hourly",3,adjust_type="modulo", adjust_value=24) ,
        "daily"    : Time_Period("daily",7) ,
        "weekly"   : Time_Period("weekly",7,adjust_type="divide", adjust_value=7) ,
        "monthly"  : Time_Period("monthly",1) ,
        "yearly"   : Time_Period("yearly",0) ,
        "minutely" : Time_Period("minutely",4,adjust_type="divide", adjust_value=5) ,
                 }


def match_sensor_to_loc(sensor):
    if sensor.id in locations:
        sensor_name = locations[sensor.id]
    else:
        sensor_name = "unk : "  + str(sensor.id)
    sensor.location = sensor_name
    return sensor_name

def init_sensor_stats(sensor):
    sensor.data          = []
    sensor.max_temp      = {}
    sensor.min_temp      = {}
    sensor.avg_temp      = {}
    for period in stats_periods.keys():
        reset_sensor_stats(sensor,period)

def reset_sensor_stats(sensor,period):
    sensor.max_temp[period] = -10000.0
    sensor.min_temp[period] =  10000.0
    sensor.avg_temp[period] =      0.0

def set_sensor_max(sensor,period,current_temp):
    sensor.max_temp[period] = max(sensor.max_temp[period],current_temp)

def set_sensor_min(sensor,period,current_temp):
    sensor.min_temp[period] = min(sensor.min_temp[period],current_temp)

def set_sensor_avg(sensor,period,current_temp):
    sensor.avg_temp[period] = ((sensor.avg_temp[period] * (record_count[period]-1)) + current_temp) \
                              / record_count[period]

def get_all_temps():
    for period in stats_periods.keys():
        record_count[period] += 1
        for sensor in all_sensors:
            sensor.last_temp = sensor.get_temperature()
            sensor.data.extend([sensor.last_temp])
            set_sensor_max(sensor,period,sensor.last_temp)
            set_sensor_min(sensor,period,sensor.last_temp)
            set_sensor_avg(sensor,period,sensor.last_temp)

    

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

output = {}
for period in stats_periods.keys():
    logfile= timestamp + r"-logfile-" + period + ".txt"
    output[period] = open(logfile,"w")

logfile = timestamp + "-records_log.txt"
output["records"] = open(logfile,"w")

all_sensors = W1ThermSensor.get_available_sensors()

record_count  = {}
last_reading  = {}

for sensor in all_sensors:
    match_sensor_to_loc(sensor)
    init_sensor_stats(sensor)

for period in stats_periods.keys():
    record_count[period] = 0
    last_reading[period] = 0
    output[period].write("%20s |" % " ")
    for sensor in all_sensors:
        output[period].write("%23s |" % sensor.location)
    output[period].write("\n")
    output[period].write("%20s |" % ("time"))
    for sensor in all_sensors:
        output[period].write("%7s %7s %7s |" % ("max","min","avg"))
    output[period].write("\n")

output["records"].write("%20s |" % ("time"))
for sensor in all_sensors:
    output["records"].write("%22s |" % sensor.location)
output["records"].write("\n")


format_str = "current %4.1f    " + \
             "max: %4.1f    " + \
             "min: %4.1f    " + \
             "avg: %4.1f    " + \
             "readings: %5d   "

#for i in range(121):
counter = 0
while counter < reading_count: 
    counter = counter + countstep
    request_time = time.time()
    timestamp = time.strftime("%Y/%m/%d-%H:%M",time.gmtime(request_time))
    get_all_temps()
    
    #print "====== " + time.asctime(time.gmtime(request_time)) + " ==== reading " + str(counter) + \
    #      " of " + str(reading_count) + " readings. ==== step is : " + str(countstep) + " ============="
    
    output["records"].write ("%20s " % (timestamp))
    
    for sensor in all_sensors:
        # -----   printing to screen   -----
        #print ("%20s : " % sensor.location),
        #for period in ("hourly","daily"):
            #print ( format_str % (sensor.last_temp,
            #                      sensor.max_temp[period],
            #                      sensor.min_temp[period],
            #                      sensor.avg_temp[period],
            #                      record_count[period]
            #               )) ,
        #print ""
        # ----- ! printing to screen   -----
        
        output["records"].write ("%23.1f " % (sensor.last_temp))
    output["records"].write("\n")
    output["records"].flush()
    #print "======================================="
    
#=======
    for period in stats_periods.keys():
        write_now = False
        period_value = stats_periods[period].get_period_values(request_time)
        data = "%20s |" % (timestamp)
        for sensor in all_sensors:
            if period_value != last_reading[period]:
                write_now = True
                data = data + "%7.1f %7.1f %7.1f |" % ( sensor.max_temp[period],
                                                        sensor.min_temp[period],
                                                        sensor.avg_temp[period] )
                reset_sensor_stats(sensor,period)
        if write_now:
            output[period].write("%s\n" % data)
            output[period].flush()
            record_count[period] = 0
            last_reading[period] = period_value    
    
    if not counter == reading_count:
        end_time=time.time()
        delay = reading_interval - ( end_time - request_time )
        time.sleep(delay)

# End of while loop.

for period in stats_periods.keys():
    output[period].write ("%20s |" % (timestamp))
    data = ""
    for sensor in all_sensors:
        data = data + "%7.1f %7.1f %7.1f |" % ( sensor.max_temp[period],
                                                sensor.min_temp[period],
                                                sensor.avg_temp[period] )
    output[period].write("%s\n" % data)
    output[period].close()

output["records"].close()
