# Copyright 2017 Xtel International Ltd.
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
    
def open_files(pre,time):
    time_s = time_format.format(time)
        
    fnacc = DATA_FILE_PATH + time_s + '_' + pre + '_acc' + DATA_FILE_EXT
    fnaud = DATA_FILE_PATH + time_s + '_' + pre + '_aud' + DATA_FILE_EXT
    fnall = DATA_FILE_PATH + time_s + '_' + pre + '_all' + DATA_FILE_EXT
    facc = open(fnacc, "w")
    faud = open(fnaud,"w")
    fall = open(fnall,"w")
    return facc,faud,fall
    
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
                
def main(pre,port,baud):
    header_len = 2
    num_temp = 1
    num_accel = 3
    num_audio = 8
    line = ''
    
    ser = open_port(port,baud)
    start = datetime.utcnow()
    facc, faud, fall = open_files(pre,start)
    unp_s, num_bytes = packet_format(header_len, num_temp, num_accel, num_audio)
    
    wait_untill_start(ser)
    ser.read(num_bytes-(header_len*2))
    
    while 1:
        dt = datetime.utcnow()
        if (dt - start).total_seconds() > 60:
            start = dt
            facc.close()
            fall.close()
            faud.close()
            facc,faud,fall = open_files(pre,start)
            
        line = ser.read(num_bytes)
        if line != "":
            unp = struct.unpack(unp_s, line)
            fall.write(','.join([str(x) for x in unp]) + "\n")
            if unp[0] == 0xAA55 and unp[1] == 0xAA55:
                facc.write(','.join([str(x) for x in unp[:(header_len+num_accel)]]) + "\n")
                faud.write('\n'.join([str(x) for x in unp[(header_len+num_accel+num_temp):]]) + "\n")
            else:
                fall.write("Packet Error ")
                facc.write('0'*(header_len+num_accel)
                faud.write('0\n'*(num_audio))
                wait_untill_start(ser)
                
    ser.close() # close port
    facc.close()
    fall.close()
    faud.close()
    
if __name__== '__main__':
    pre = sys.argv[1]
    port = int(sys.argv[2])
    baud = int(sys.argv[3])
    main(pre,port,baud)
