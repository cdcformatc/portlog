import serial
import sys
from datetime import datetime
import struct
import time
import gzip

time_format = "{0:%Y}{0:%m}{0:%d}{0:%H}{0:%M}"
    
def packet_format(header,temp,accel,audio):
    unp = ('<' +
        'H' * header +
        'h' * temp +
        'h' * accel +
        'h' * audio)
    return unp, (len(unp)-1)*2
    
def open_files(outpath,time):
    time_s = time_format.format(time)
    fnall = outpath + time_s + '_all.txt.gz'
    
    fall = gzip.open(fnall, 'wb')
    return fall
    
def open_port(port,baud):
    ser = None
    while ser==None:
        try:
            ser = serial.Serial(port, baudrate=baud, timeout=1.1)  # open first serial port
        except serial.serialutil.SerialException:
            print "Can not open port, trying again in 5 second"
            ser = None
            time.sleep(5)
    print "Connected to",ser.portstr  # check which port is used
    return ser
    
def wait_untill_start(ser):
    while 1:
        x = ser.read(1)
        if x == '':
            continue
        if ord(x) == 0x55:
            y = [ord(c) for c in ser.read(3)]
            if y[0] == 0xAA and y[1] == 0x55 and y[2] == 0xAA:
                break
                
def main(outpath,port,baud):
    header_len = 2
    count_len = 1
    num_temp = 1
    num_accel = 3
    num_audio = 4
    line = ''
    
    ser = open_port(port,baud)
    start = datetime.utcnow().replace(second=0, microsecond=0)
    fall = open_files(outpath,start)
    unp_s, num_bytes = packet_format(header_len+count_len, num_temp, num_accel, num_audio)
    
    wait_untill_start(ser)
    ser.read(num_bytes-(header_len*2))
    
    while 1:
        dt = datetime.utcnow()
        if (dt - start).total_seconds() > 60:
            start = dt
            fall.close()
            fall = open_files(outpath,start)
            
        line = ser.read(num_bytes)
        if line != "":
            unp = struct.unpack(unp_s, line)
            fall.write(','.join([str(x) for x in unp]) + "\n")
            if unp[0] == 0xAA55 and unp[1] == 0xAA55:
                pass
            else:
                fall.write("Packet Error\n")
                wait_untill_start(ser)
                ser.read(num_bytes-(header_len*2))
                
    ser.close() # close port
    fall.close()
    
if __name__== '__main__':
    outpath = sys.argv[1]
    port = sys.argv[2]
    baud = int(sys.argv[3])
    main(outpath,port,baud)
