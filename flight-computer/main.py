import serial
import time
import datetime
import os
import mysql.connector as mariadb
import array
import struct as struct
import logging
from struct import *

from connectionsAndCommands import *
from dataBaseStorage import *
from logPWNSweep import *

# Track status of each servo
actuatorStatus = False
motorStatus = False
# Serial objects that control serial communication with HASP and the Arduino. To be used as global variables.
haspSerial = None
arduinoSerial = None
# Logger setup
FORMAT = '[%(asctime)-15s] %(name)s.%(levelname)s: %(message)s'
formatter = logging.Formatter(FORMAT)
logging.basicConfig(filename='serial.log', filemode='a', level=logging.INFO, format=FORMAT)
logger = logging.getLogger()

# Create console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

if __name__ == '__main__':
    try:
        haspSerial = connectToHASP()
        arduinoSerial = connectToArduino()
        while True:
            if haspSerial is not None and arduinoSerial is not None:
                processCommands()
                #testSerialArduino()
                #storeDataInDatabase() 
            else:
                if haspSerial is None and arduinoSerial is None:
                    raise Exception('Missing serial connection to HASP and Arduino.')
                elif haspSerial is None:
                    raise Exception('Missing serial connection to HASP.')
                elif arduinoSerial is None:
                    raise Exception('Missing serial connection to Arduino.')
    except Exception as e:
        logging.error(e)
    
    #This will be removed later, placed it here because of the absence of a haspSerial connection
    storeDataInDatabase()