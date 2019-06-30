import serial
import time
import datetime
import os
import mysql.connector as mariadb
import array
import struct as struct
import logging
from struct import *

#Passing an array that holds voltage values
#Voltage/current sweep will occur every 30 minutes. All other data will be stored every second onto the database
def voltageSweep(voltages):
    UTCTimeString = str(datetime.datetime.now() + ".csv")
    f = open(UTCTimeString, "w+")
    # Writes to the newly created csv file
    with open(UTCTimeString, mode='w+') as UTC_File:
        data_writer = csv.writer(UTC_File, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow(['Voltage'])

        for i in range(0, voltages.len()): #stores all of the voltages a csv file
            data_writer.writerow([voltages[i]])
