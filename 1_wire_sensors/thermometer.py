import time
from w1thermsensor import W1ThermSensor
# To get w1thermsensor :
# git clone https://github.com/timofurrer/w1thermsensor.git && cd w1thermsensor
# sudo python setup.py install

locations = {
  "000005eb8b82" : "Pi",
  "0000062ac658" : "Wall",
  "0000062caad9" : "Window",
}

logfile=r"logfile.txt"
output = open(logfile,"w")

def match_sensor_to_loc(sensor_id):
    if sensor_id in locations:
        return locations[sensor_id]
    else:
        return "unknown location"

all_sensors = W1ThermSensor.get_available_sensors()
for sensor in all_sensors:
    sensor.location = match_sensor_to_loc(sensor.id)
    print("Sensor %s @ location %s has temperature %.2f" % (sensor.id, sensor.location, sensor.get_temperature()))
    output.write("%s " % sensor.location)

output.write("\n")



#for i in range(121):
i = 0
while 1:
    i = i + 1
    print "==========\nstep "+str(i)
    
    for sensor in all_sensors:
        print ("%20s : %3.1f" % (sensor.location, sensor.get_temperature()))
        output.write ("%6.2f " % sensor.get_temperature())
    output.write("\n")
    output.flush()
    time.sleep(15)

close(output)
