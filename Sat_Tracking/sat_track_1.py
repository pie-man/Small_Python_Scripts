#!/usr/bin/env python2.7

import ephem
from datetime import datetime, timedelta

# DATA - in this case TLE for satellites of interest...
suomi_npp_tle = ["SUOMI NPP",
       "1 37849U 11061A   18102.92280612 -.00000005 +00000-0 +18457-4 0  9997",
       "2 37849 098.7329 042.2875 0001446 061.4714 340.0509 14.19544734334628"]

iss_tle = ["ISS",
       "1 25544U 98067A   18103.52382522  .00025144  00000-0  38373-3 0  9995",
       "2 25544  51.6440 341.0761 0002169 351.2480  69.1597 15.54280591108461"]

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
    return observer

if __name__ == '__main__':

    # create an 'observer' at the met office.
    met_office = create_an_observer("Met Office", '50.727323', '-3.474555')
    met_office.date = '2018/4/13 14:00'
    met_office.date = datetime.now()+ timedelta(hours=-2)

    #create a 'body' based on the TLE ofr a satellite.
    suomi_npp = ephem.readtle(*suomi_npp_tle)
    suomi_npp.compute(met_office)

    print_basics(suomi_npp, met_office)

    #create a 'body' based on the TLE ofr a satellite.
    iss = ephem.readtle(*iss_tle)
    iss.compute(met_office)

    print_basics(iss, met_office)
