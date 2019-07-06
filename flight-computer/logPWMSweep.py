import serial
import time
import os
import array
import struct as struct
import logging
import csv
from datetime import datetime
from struct import *
from serialconnections.serialconnections import packetHandler

# Logger setup
logger = logging.getLogger('pwm_read')
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

PWM_SWEEP_BYTE1 = b'\x51'
PWM_SWEEP_BYTE2 = b'\x52'
PWM_CMD = PWM_SWEEP_BYTE1 + PWM_SWEEP_BYTE2

previousSweepTime = None
time_fmt = '%Y-%m-%d %H:%M:%S'


def checkPWMTime(arduino_serial_conn):
    global previousSweepTime
    logger.info("Checking PWM time.")    
    currentTime = datetime.strptime(datetime.now().strftime(time_fmt), time_fmt)
    currentTime_ts = time.mktime(currentTime.timetuple())
    if previousSweepTime is not None:
        print(int(currentTime_ts - previousSweepTime))
    if previousSweepTime is None or int(currentTime_ts - previousSweepTime) >= 30:
        previousSweepTime = currentTime_ts
        performSweep(arduino_serial_conn)


def performSweep(arduino_serial_conn):
    logger.info("Performing PWM sweep.")
    
    # Send command to the Arduino to perform sweep
    arduino_serial_conn.write(PWM_CMD)
    """
    pwm_packet = packetHandler(arduino_serial_conn)
    if pwm_packet is not None:
        pwm_array = pwm_packet.split(',')
        print(pwm_array)
        return pwm_array
    """

#Assuming the names of the folders are 1,2,3 etc.

#Path to the solar cell folders
savePath = "/home/pi/Desktop/flightComputer/"

pwmString = "begin_pwm,4,1.00,3.65,5.654,6.45,begin_pwm,5,1.00,2.44,5.55,3.33,begin_pwm,6,2.55,3.44,4.33,2.44"

def storeInCSVFiles(pwmString):
    UTCTimeString = "/" + str(datetime.datetime.now()) + ".csv"
    i=0
    
    while i<len(pwmString):
        if(pwmString[i] == 'b'):
            i = i+10
            temporarySavePath = savePath + pwmString[i]
            i = i + 2
        else:
            break
       
        with open(temporarySavePath + UTCTimeString, mode='w+') as UTC_File:
            data_writer = csv.writer(UTC_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)       
            while i<len(pwmString):              
                if pwmString[i] == 'b':
                    break   
                else:
                    UTC_File.write(pwmString[i])      
                    i = i + 1

#storeInCSVFiles(pwmString)    

