import time

class Thermometer:
    '''defines a DS18B20 thermometer'''
    def __init__(self,name,id):
        self.name = name
        self.id = id
    def read_temp(self):
        filename = "/sys/bus/w1/devices/" + self.id + "/w1_slave"
        tempfile = open (filename)
        fulltext = tempfile.read()
        tempfile.close()
        tempdata = fulltext.split("\n")[1].split(" ")[9]
        temperature = float(tempdata[2:])
        temperature = temperature / 1000
        return temperature

therm1 = Thermometer("Window","28-0000062caad9")
therm2 = Thermometer("wall",  "28-0000062ac658")
therm3 = Thermometer("Pi",    "28-000005eb8b82")

#for i in range(121):
i = 0
while 1:
    i = i + 1
    print "==========\nstep "+str(i)
    
    print ("{:10} {:3.1f}".format(therm1.name, therm1.read_temp()))
    print ("{:10} {:3.1f}".format(therm2.name, therm2.read_temp()))
    print ("{:10} {:3.1f}".format(therm3.name, therm3.read_temp()))
    time.sleep(15)


