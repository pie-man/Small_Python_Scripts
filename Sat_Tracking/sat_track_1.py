#!/usr/bin/env python2.7

import ephem
from datetime import datetime, timedelta
import urllib2
import re

# get lists of TLEs from celestrak.com
weather_sats_file = "http://celestrak.com/NORAD/elements/weather.txt"
#NOAA_sats_file = "http://celestrak.com/NORAD/elements/noaa.txt"
#GEOS_sats_file = "http://celestrak.com/NORAD/elements/goes.txt"
Earth_Resources_sats_file = "http://celestrak.com/NORAD/elements/resource.txt"
space_stations = "http://celestrak.com/NORAD/elements/stations.txt"

def print_basics(body, observer, time=ephem.now()):
    observer.date = time
    body.compute(observer)
    
    print("From the vantage point of {0:s} the next pass of {1:s}"
          .format(observer.name, body.name) + 
          " will be on {0:s}".format(ephem_time_to_datetime_string(
               body.rise_time,'%d of %b %Y')))
    print("rising @ {0:s}, transit @ {1:s} and set @ {2:s}\n"
          .format(ephem_time_to_datetime_string(body.rise_time,'%H:%M'),
                  ephem_time_to_datetime_string(body.transit_time,'%H:%M'),
                  ephem_time_to_datetime_string(body.set_time,'%H:%M')))

def ephem_time_to_datetime_string(ephem_time, format_str):
    ephem_format = "%Y/%m/%d %H:%M:%S"
    time = ephem.localtime(ephem_time)
    #time = datetime.strptime(str(ephem_time), ephem_format)
    return datetime.strftime(time, format_str)

def create_an_observer(name, lattitude, longitude):
    observer = ephem.Observer()
    observer.name = name
    observer.long, observer.lat = longitude, lattitude
    observer.date = ephem.now()
    return observer

def get_TLEs_from_net(target_url):
    TLE_data = urllib2.urlopen(target_url).read(20000)
    TLE_data = TLE_data.split("\n")
    return TLE_data

def find_sat_in_list(satname, TLE_data):
    sat_TLE = []

    for index, line in enumerate(TLE_data):
        if re.search(satname, line, re.IGNORECASE):
            sat_TLE.append(line.strip())
            sat_TLE.append( TLE_data[index + 1].strip() )
            sat_TLE.append( TLE_data[index + 2].strip() )
            #for line in sat_TLE:
            #    print(line)
            #print("")
            break
    return sat_TLE
    
def create_list_of_angles(body, observer):
    current_time = body.rise_time
    end_time = body.set_time
    format_string = ("  @ {0:5s} it will be at {1:>11s} degrees north and " +
                     " {2:>10s} degrees above horizon.")
    while current_time < end_time:
        observer.date = ephem.date(current_time)
        body.compute(observer)
        time = ephem_time_to_datetime_string(ephem.date(current_time), '%H:%M')
        print(format_string.format(time, str(body.az), str(body.alt)))
        current_time = current_time + ephem.minute
    print("")
    
if __name__ == '__main__':

    # create an 'observer' at the met office.
    met_office = create_an_observer("Met Office", '50.727323', '-3.474555')

    #print ("Ephem's date stamp is ...     {0:}".format(ephem.now()))
    #print ("Datetimes's date stamp is ... {0:}".format(met_office.date))

    sat_to_find = "SUOMI NPP"

    weather_sats_TLEs = get_TLEs_from_net(weather_sats_file)
    suomi_npp_tle = find_sat_in_list(sat_to_find, weather_sats_TLEs)

    space_stations_TLEs = get_TLEs_from_net(space_stations)
    iss_tle = find_sat_in_list("ISS", space_stations_TLEs)

    #create a 'body' based on the TLE of a satellite.
    if suomi_npp_tle:
        suomi_npp = ephem.readtle(*suomi_npp_tle)
        suomi_npp.compute(met_office)

        print_basics(suomi_npp, met_office)

        create_list_of_angles(suomi_npp, met_office)
    else:
        print("Could not find suomi_npp in data provided")

    #create a 'body' based on the TLE of the ISS.
    if iss_tle:
        iss = ephem.readtle(*iss_tle)
        iss.compute(met_office)

        print_basics(iss, met_office)

        create_list_of_angles(iss, met_office)
    else:
        print("Could not find iss in data provided")

    sat_TLEs = []
    sat_name_list = [
                     "NOAA 15",
                     "NOAA 18",
                     "NOAA 19",
                     "NOAA 20",
                     "Suomi NPP",
                     "AQUA",
                     "TERRA",
                     "METOP-A",
                     "METOP-B",
                     "FENGYUN 3A",
                     "FENGYUN 3B",
                    ]
    data_sources = [(weather_sats_file,"weather_sats_file"),
                    #(NOAA_sats_file,"NOAA_sats_file"),
                    #(GEOS_sats_file,"GEOS_sats_file"),
                    (Earth_Resources_sats_file, "Earth_Resources_sats_file"),
                    (space_stations,"space_stations")]
    sat_tles = {}
    for source in data_sources:
        TLEs =  get_TLEs_from_net(source[0])
        print("In the source file {0:s} I found.....".format(source[1]))
        for sat_name in sat_name_list:
            tle = find_sat_in_list(sat_name, TLEs)
            if tle:
                print(   "... {0:s}".format(sat_name))
                sat_tles[sat_name] = tle
                #for line in tle:
                #    print(line)
                #print("")
            #else:
            #    print("Could not find {0:s} in data provided".format(sat_name))

    next_pass = ephem.now() + (24 * ephem.hour)
    for sat_name in sat_name_list:
        print("Looking at : {0:s}".format(sat_name))
        for line in sat_tles[sat_name]:
            print(line)
        sat_body = ephem.readtle(*sat_tles[sat_name])
        met_office.date = ephem.now()
        sat_body.compute(met_office)
        print("{0:s} rises at {1:s}".format(sat_name,
         ephem_time_to_datetime_string(sat_body.rise_time, '%Y/%m/%d %H:%M')))
        if sat_body.rise_time < next_pass:
            next_pass = sat_body.rise_time
            next_sat = sat_name
        print("")
    print("The next body to track is {0:s} at {1:s}".format(next_sat,
          ephem_time_to_datetime_string(ephem.date(next_pass), '%Y/%m/%d %H:%M')))
        
