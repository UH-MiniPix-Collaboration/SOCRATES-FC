import serial
import time
import datetime
import os
import mysql.connector as mariadb
import array
import struct as struct
import logging
import csv

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


def checkPWMTime(arduino_serial_conn):
    global previousSweepTime
    logger.info("Checking PWM time.")
    logger.info(previousSweepTime)
    if previousSweepTime is None or (datetime.datetime.now().second - previousSweepTime.second) >= 30:
        previousSweepTime = datetime.datetime.now()
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

    
#Stores the voltage values receieved from the arduino into csv files with the name as the timestamp
def storeInCSVFies(voltages):
    UTCTimeString =  str((datetime.datetime.now()+ ".csv"))

    # Writes to the newly created csv file
    with open(UTCTimeString, mode='w+') as UTC_File:
        data_writer = csv.writer(UTC_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow(['Voltage'])

        for i in range(0, len(voltages)): #stores all of the voltages in a csv file
            data_writer.writerow([voltages[i]])

for i in range(0,12):
    voltageSweep("solar" + str(i))

