#!/usr/bin/env python

#import sqlite3
import MySQLdb
import datetime
from time import sleep
import urllib2

SQL_LIGHT_DBNAME = '/home/pi/Python/Temp_logging/test.db'

# get temerature
# argument devicefile is the path of the sensor to be read,
# returns None on error, or the temperature as a float

SENSORS = {
      'Kitchen'       : '28-0000062ac658',
      'K Radiator'    : '28-000005fb0405',
      'Boiler Out'    : '28-0000062caad9',
      'Boiler Return' : '28-000005fb2cc1',
}

THINGSPEAK_MAP = {
      'Kitchen'       : 'field5',
      'K Radiator'    : 'field6',
      'Boiler Out'    : 'field7',
      'Boiler Return' : 'field8',
}

TIMES={
    datetime.datetime(1900,1,1, 0, 0) : 15,
    datetime.datetime(1900,1,1, 5,40) : 20,
    datetime.datetime(1900,1,1, 8,00) : 12,
    datetime.datetime(1900,1,1,12,00) : 13,
    datetime.datetime(1900,1,1,13,30) : 12,
    datetime.datetime(1900,1,1,17, 0) : 20,
    datetime.datetime(1900,1,1,22,30) : 15,
}

BUS_PATH = '/sys/bus/w1/devices/'

baseURL = "https://api.thingspeak.com/update?api_key=HQQCX6G82PXR55I8"

def get_temp(sensor_id):
    if sensor_id == 'Thermostat':
        temp = get_thermostat_setting(datetime.datetime.now())
    else:
        temp = read_sensor_temp(sensor_id)
    return temp

def read_sensor_temp(sensor_id):
    devicefile = BUS_PATH + sensor_id + '/w1_slave'
    try:
        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        return None
    # get the status from the end of line 1 
    status = lines[0].split()[-1]
    # is the status is ok, get the temperature from line 2
    if status=="YES":
        #print status
        tempstr= lines[1].split()[-1][2:]
        tempvalue=float(tempstr)/1000
        #print tempvalue
        return tempvalue
    else:
        print "There was an error.", devicefile
        return None

def get_thermostat_setting(time_now):
    temp = None
    for set_time , targ_temp in sorted(TIMES.iteritems()):
        #print ("At {0:} I reset the targ_temp to {1:d}".format(set_time,targ_temp))
        if time_now.time() > set_time.time():
            temp = targ_temp
    return temp

# store the temperature in the database
def log_temperature_sql(dbname, sensor_label, temp):
    if sensor_label is None or temp is None:
        print("Error pushing data to db. None value supplied")
        return
    try: 
        conn=sqlite3.connect(dbname)
        curs=conn.cursor()
    except:
        print("Error opening db for write. No database found " +
	      "- or connectin refused")
        return
    curs.execute("INSERT INTO temps values(date('now'), time('now'), (?), (?))",
                 (sensor_label,temp))
    # commit the changes
    conn.commit()
    conn.close()


def print_temps(dbname, zone):
    try:
       conn = sqlite3.connect(dbname)
       curs = conn.cursor()
    except:
        print("Error opening db for read. No database found " +
	      "- or connectin refused")
        return
    for row in curs.execute("SELECT * FROM temps WHERE zone = '{0:s}'"
                            .format(zone)):
        print("{0:10s} {1:8s}  :  {3:4.2f}".format( *row ))
    conn.close()

def report_to_screen(temp_readings):
    report_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M")
    for location, temp in sorted(temp_readings.iteritems()):
        report_string += "  {0:10.1f}".format(temp)
    print(report_string)

def report_to_screen_header(temp_readings):
    report_string = " Time         "
    for location, temp in sorted(temp_readings.iteritems()):
        report_string += "  {0:>10s}".format(location[:10])
    print(report_string)

def report_to_mysql(temp_readings):
    try: 
        conn=MySQLdb.connect("192.168.1.104", "temp_log", "M4rv1n", "temp_logs")
        curs=conn.cursor()
    except:
        print("Error opening mysql db for write. No database found " +
	      "- or connection refused")
        return
    try:
        timestamp = datetime.datetime.now()
        for location, temp in temp_readings.iteritems():
            if location is None or temp is None:
                print("Error pushing data to mysql db. None value supplied")
                continue
	    sql = "INSERT INTO temp_readings(date, time, \
	            temp, location)" +\
	           "VALUES('{0:s}','{1:s}','{2:8.3f}','{3:s}')".format(
	           str(timestamp.date()), str(timestamp.strftime("%H:%M:%S")),
	           temp, location)
            #print(sql)
            curs.execute(sql)
        # commit the changes
        conn.commit()
    except:
        print("Error writing to mysql db. Something went wrong....")
        conn.rollback()
    conn.close()

def report_to_sqlight(temp_readings):
    try: 
        conn=sqlite3.connect(SQL_LIGHT_DBNAME)
        curs=conn.cursor()
    except:
        print("Error opening sqlite db for write. No database found " +
	      "- or connection refused")
        return
    try:
        for location, temp in temp_readings.iteritems():
            if location is None or temp is None:
                print("Error pushing data to sqlite db. None value supplied")
                continue
            #log_temperature_sql(SQL_LIGHT_DBNAME, location, temp)
            #print("PostIF : Location : {0:12s}     T : {1:8.3f}".format(location, temp))
            curs.execute("INSERT INTO temps values(date('now'), time('now'), (?), (?))",
                         (location,temp))
        # commit the changes
        conn.commit()
    except:
        print("Error writing to sqlite db. Something went wrong....")
        conn.rollback()
    conn.close()

def report_to_thingspeak(temp_readings):
    thingspeak_string = ''
    for location, temp in temp_readings.iteritems():
        if THINGSPEAK_MAP[location] is None or temp is None:
	    continue
	temp_log_str = "&{0:s}={1:}".format(THINGSPEAK_MAP[location], temp)
	thingspeak_string += temp_log_str
	#print (temp_log_str)
    g = urllib2.urlopen(baseURL + thingspeak_string)


def main():
    temp_readings = {}
    start_time = datetime.datetime.now()
    for location, sensor_id in SENSORS.iteritems():
        temp_readings[location] = get_temp(sensor_id)
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    log_time = start_time + duration/2

    report_to_thingspeak(temp_readings)
    #report_to_sqlight(temp_readings)
    report_to_mysql(temp_readings)
    #report_to_screen_header(temp_readings)
    #report_to_screen(temp_readings)

if __name__ == "__main__":
   main()
