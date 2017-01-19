import serial
import sys
from datetime import datetime
import struct

port = int(sys.argv[1])
ser = serial.Serial(port, baudrate=230400, timeout=1)  # open first serial port
print "Connected to",ser.portstr  # check which port is used
line = ''

start = datetime.utcnow()
path = "data"
fn = '{1}/{0:%Y}{0:%m}{0:%d}{0:%H}{0:%M}.txt'.format(start,path)
f = open(fn,"w")
print fn

while 1:
    dt = datetime.utcnow()
    
    if (dt - start).total_seconds() > 60:
        start = dt
        f.close()
        fn = '{1}/{0:%Y}{0:%m}{0:%d}{0:%H}{0:%M}.txt'.format(start,path)
        f = open(fn,"w")
        print fn
    
    line = ser.read(8)
    if line!="":
        unp = struct.unpack('<Hhhh', line)

        i = unp[0]
        x = unp[1]
        y = unp[2]
        z = unp[3]

        f.write("{},{},{},{}\n".format(i,x,y,z))

ser.close()             # close port
