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
        logger.debug(str(int(currentTime_ts - previousSweepTime)) + ' seconds remaining until next sweep.')
    if previousSweepTime is None or int(currentTime_ts - previousSweepTime) >= 60:
        previousSweepTime = currentTime_ts
        performSweep(arduino_serial_conn)


def performSweep(arduino_serial_conn):
    logger.info("Performing PWM sweep.")
    
    # Send command to the Arduino to perform sweep
    arduino_serial_conn.write(PWM_CMD)

    
#Assuming the names of the folders are 1,2,3 etc.

#Path to the solar cell folders
directoryPath = os.getcwd()

#pwmString = "begin_pwm,4,1.00,3.65,5.654,6.45,begin_pwm,5,1.00,2.44,5.55,3.33,begin_pwm,6,2.55,3.44,4.33,2.44"

def storeInCSVFiles(pwmString):
    UTCTime = "/" + str(datetime.now()) + ".csv"
    strings = pwmString.split('begin_pwm,')
    strings.pop(0)  # Get rid of the residual index
    for cellString in strings:
        #cell_num = cellString.split(',')[0]
        i=0
        while i<len(cellString):
            print(cellString)
            print('Cell num: ' + cellString[i])
            temporaryPath = directoryPath + '/' + cellString[i]
            i = i + 2
            
            with open(temporaryPath + UTCTime, mode='w+') as UTC_File:
                data_writer = csv.writer(UTC_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                #UTC_File.write(pwmString.split(cell_num+',')[1])
                
                while i<len(cellString):
                    UTC_File.write(cellString[i])      
                    i = i + 1
    
                
#storeInCSVFiles(pwmString)    

