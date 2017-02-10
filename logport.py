import serial
import sys
from datetime import datetime
import struct
import time

port = int(sys.argv[1])
baud = int(sys.argv[2])
ser = None

while ser==None:
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=1.1)  # open first serial port
    except serial.serialutil.SerialException:
        print "Can not open port, trying again in 5 second"
        ser = None
        time.sleep(5)
print "Connected to",ser.portstr  # check which port is used
line = ''

path = 'data'
ext = 'txt'
fn_pattern = "{1}/{0:%Y}{0:%m}{0:%d}{0:%H}{0:%M}_{2}.{3}"

start = datetime.utcnow()
fnacc = fn_pattern.format(start,path,'acc',ext)
fnaud = fn_pattern.format(start,path,'aud',ext)
fnall = fn_pattern.format(start,path,'all',ext)
facc = open(fnacc, "w")
faud = open(fnaud,"w")
fall = open(fnall,"w")
print fnacc,fnaud

header_len = 1
num_temp = 1
num_accel = 3
num_audio = 8

num_ints = header_len + num_temp + num_accel + num_audio 
num_bytes = num_ints*2

unp_s = '<' + 'H' * header_len \
    + 'h' * num_temp \
    + 'h' * num_accel \
    + 'h' * num_audio
    
print unp_s

while 1:
    dt = datetime.utcnow()
    
    if (dt - start).total_seconds() > 60:
        start = dt
        facc.close()
        faud.close()
        fnacc = fn_pattern.format(start,path,'acc',ext)
        fnaud = fn_pattern.format(start,path,'aud',ext)
        fnall = fn_pattern.format(start,path,'all',ext)
        facc = open(fnacc, "w")
        faud = open(fnaud,"w")
        fall = open(fnall,"w")
        print fnacc,fnaud,fnall
    
    
    line = ser.read(num_bytes)
    if line!="":
        unp = struct.unpack(unp_s, line)
        
        facc.write(','.join([str(x) for x in unp[:4]])+"\n")
        faud.write('\n'.join([str(x) for x in unp[5:]])+"\n")
        fall.write(','.join([str(x) for x in unp])+"\n")
        
ser.close()             # close port
