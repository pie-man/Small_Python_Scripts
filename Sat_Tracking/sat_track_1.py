#!/usr/bin/env python2.7

import ephem
from datetime import datetime, timedelta
import urllib2
import re

# DATA - in this case TLE for satellites of interest...
suomi_npp_tle = ["SUOMI NPP",
       "1 37849U 11061A   18106.18442330  .00000010  00000-0  25684-4 0  9991",
       "2 37849  98.7334  45.5038 0001382  59.2898  80.8941 14.19545053335072"]

iss_tle = ["ISS",
       "1 25544U 98067A   18103.52382522  .00025144  00000-0  38373-3 0  9995",
       "2 25544  51.6440 341.0761 0002169 351.2480  69.1597 15.54280591108461"]

# get TLEs from celestrak.com
weather_sats_file = "http://celestrak.com/NORAD/elements/weather.txt"
NOAA_sats_file = "http://celestrak.com/NORAD/elements/noaa.txt"
GEOS_sats_file = "http://celestrak.com/NORAD/elements/goes.txt"
Earth_Resources_sats_file = "http://celestrak.com/NORAD/elements/resource.txt"
space_stations = "http://celestrak.com/NORAD/elements/stations.txt"

def print_basics(body, observer):
    body.compute(observer)
    print("From the vantage point of {0:s}:\n"
          .format(observer.name))
    print(" The next rise of {0:s} will be {1:}"
          .format(body.name,body.rise_time))
    print(" The next transition of {0:s} will be {1:}"
          .format(body.name,body.transit_time))
    print(" The next setting of {0:s} will be {1:}\n"
          .format(body.name,body.set_time))

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
             print(sat_TLE)
             break
    return sat_TLE
    
def create_list_of_angles(body, observer):
    observer.date = ephem.now()
    body.compute(observer)
    start_time = body.rise_time
    duration_time = body.transit_time
    end_time = body.set_time
    current_time = start_time
    observer.date = current_time
    body.compute(observer)
    #print("    The current time is      ... {0:}".format(current_time))
    #print("    The declination is     ..... {0:}".format(body.dec))
    #print("    The right ascension is ..... {0:}".format(body.ra))
    #print("    The azimuth is         ..... {0:}".format(body.az))
    #print("    The altitude is        ..... {0:}".format(body.alt))
    print("  @ {0:} it will be at {1:} degrees north and {2:} degrees above horizon.".format(current_time, body.az, body.alt))
    #print("".format())
    while current_time < end_time:
        current_time = current_time + ephem.minute
        observer.date = ephem.date(current_time)
        body.compute(observer)
        #print("    The current time is      ... {0:}".format(ephem.date(current_time)))
        #print("    The declination is     ..... {0:}".format(body.dec))
        #print("    The right ascension is ..... {0:}".format(body.ra))
        #print("    The azimuth is         ..... {0:}".format(body.az))


        #print("    The altitude is        ..... {0:}".format(body.alt))
        print("  @ {0:} it will be at {1:} degrees north and {2:} degrees above horizon.".format(ephem.date(current_time), body.az, body.alt))
    
if __name__ == '__main__':

    # create an 'observer' at the met office.
    met_office = create_an_observer("Met Office", '50.727323', '-3.474555')
    #met_office.date = '2018/4/13 14:00'
    #met_office.date = datetime.now() + timedelta(hours=-1)
    #print ("Ephem's date stamp is ...     {0:}".format(ephem.now()))
    #print ("Datetimes's date stamp is ... {0:}".format(met_office.date))

    #create a 'body' based on the TLE ofr a satellite.
    suomi_npp = ephem.readtle(*suomi_npp_tle)
    suomi_npp.compute(met_office)

    print_basics(suomi_npp, met_office)

    #create a 'body' based on the TLE ofr a satellite.
    iss = ephem.readtle(*iss_tle)
    iss.compute(met_office)

    print_basics(iss, met_office)

    
    create_list_of_angles(iss, met_office)

    sat_to_find = "SUOMI NPP"

    weather_sats_TLEs = get_TLEs_from_net(weather_sats_file)
    suomi_npp_tle = find_sat_in_list(sat_to_find, weather_sats_TLEs)

    if suomi_npp is not None:
        suomi_npp_2 = ephem.readtle(*suomi_npp_tle)
        suomi_npp_2.compute(met_office)

        print_basics(suomi_npp_2, met_office)
    else:
        print("Could not find suomi_npp in data provided")
