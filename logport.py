import serial
import sys
from datetime import datetime
import struct
import time

DATA_FILE_PATH = 'data/'
DATA_FILE_EXT = '.txt'
time_format = "{0:%Y}{0:%m}{0:%d}{0:%H}{0:%M}"

def packet_format(header,temp,accel,audio):
    unp = ('<' +
        'H' * header +
        'h' * temp +
        'h' * accel +
        'h' * audio)
        
    return unp, (len(unp)-1)*2
    
def open_files(time):
    time_s = time_format.format(time)
    fnacc = DATA_FILE_PATH + time_s + '_acc' + DATA_FILE_EXT
    fnaud = DATA_FILE_PATH + time_s + '_aud' + DATA_FILE_EXT
    fnall = DATA_FILE_PATH + time_s + '_all' + DATA_FILE_EXT
    
    facc = open(fnacc, "w")
    faud = open(fnaud,"w")
    fall = open(fnall,"w")
    return facc,faud,fall
    
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

start = datetime.utcnow()
facc,faud,fall = open_files(start)

header_len = 1
num_temp = 1
num_accel = 3
num_audio = 8
    
unp_s, num_bytes = packet_format(header_len,num_temp,num_accel,num_audio)

while 1:
    dt = datetime.utcnow()
    
    if (dt - start).total_seconds() > 60:
        start = dt
        facc.close()
        fall.close()
        faud.close()
        facc,faud,fall = open_files(start)
    
    line = ser.read(num_bytes)
    if line!="":
        unp = struct.unpack(unp_s, line)
        
        facc.write(','.join([str(x) for x in unp[:4]])+"\n")
        faud.write('\n'.join([str(x) for x in unp[5:]])+"\n")
        fall.write(','.join([str(x) for x in unp])+"\n")
        
ser.close()             # close port
