import serial
import time
import os
import mysql.connector as mariadb
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

    
"""
Currently stores csv files in the same directory

solar1 = [1,1,1]
solar2 = [2,2,2]
solar3 = [3,3,3]
solar4 = [4,4,4]
solar5 = [5,5,5]
solar6 = [6,6,6]
solar7 = [7,7,7]
solar8 = [8,8,8]
solar9 = [9,9,9]
solar10 = [10,10,10]
solar11 = [11,11,11]
solar12 = [12,12,12]
"""
#Stores the voltage values receieved from the arduino into csv files with the name as the timestamp
def storeInCSVFiles(voltages, solarCellNumber):
    UTCTimeString =  str(solarCellNumber) + str(datetime.now())
    print(UTCTimeString)
    
    UTCTimeString = UTCTimeString+".csv"
    # Writes to the newly created csv file
    with open(UTCTimeString, mode='w+') as UTC_File:
        data_writer = csv.writer(UTC_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow(['Voltage'])

        for i in range(0, len(voltages)): #stores all of the voltages in a csv file
            data_writer.writerow([voltages[i]])

"""            
storeInCSVFiles(solar1, "solarOne-")
storeInCSVFiles(solar2, "solarTwo-")
storeInCSVFiles(solar3, "solarThree-")
storeInCSVFiles(solar4, "solarFour-")
storeInCSVFiles(solar5, "solarFive-")
storeInCSVFiles(solar6, "solarSix-")
storeInCSVFiles(solar7, "solarSeven-")
storeInCSVFiles(solar8, "solarEight-")
storeInCSVFiles(solar9, "solarNine-")
storeInCSVFiles(solar10, "solarTen-")
storeInCSVFiles(solar11, "solarEleven-")
storeInCSVFiles(solar12, "solarTwelve-")
"""
