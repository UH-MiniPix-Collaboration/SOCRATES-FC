import serial
import time
import datetime
import os
import mysql.connector as mariadb
import array
import struct as struct
import logging
from struct import *

from main import *

def rebootPi():
    os.system('sudo shutdown -r now') # Reboot the Pi and consequently the Arduino

# Open connection with a specified port
def connectPort(portName):
    ser = None
    try:
        ser = serial.Serial(port = portName, baudrate = 4800, parity = serial.PARITY_NONE)
        if ser != None:
            logging.info('Successfully connected to port \'' + ser.name + '\' with baudrate ' + str(ser.baudrate) + '.')
        else:
            logging.warning('Could not connect to port ' + portName + '.')
    except Exception as e:
        logging.error('Error while attempting to open serial port \'' + portName + '\'.')
        logging.error(e)
    return ser

def connectToHASP():
    global haspSerial
    logging.info('Attempting connection with HASP.')
    usbPortName = ''
    dirList = os.listdir('/dev/')
    # Find all ttyUSB devices (i.e. connection via RS232)
    for name in dirList:
        if 'USB' in name:
            usbPortName = '/dev/' + name
            logging.info('Found USB port: ' + str(usbPortName))
            break
    haspSerial = connectPort(usbPortName)
    return '/dev/'

def connectToArduino():
    global arduinoSerial
    logging.info('Attempting connection with Arduino.')
    acmPortName = ''
    dirList = os.listdir('/dev/')
    # Find all ttyACM devices (i.e. connection to Arduino)
    for name in dirList:
        if 'ACM' in name:
            acmPortName = '/dev/' + name
            logging.info('Found ACM port: ' + str(acmPortName))
            break
    arduinoSerial = connectPort(acmPortName)
    return arduinoSerial

# Checks for commands from HASP and sends them to the Arduino
def processCommands():
    global actuatorStatus
    global motorStatus
    #logging.info('Checking for commands.')
    if haspSerial.in_waiting > 0:
        bufSize = haspSerial.in_waiting
        command = haspSerial.read(bufSize)
        logging.info('Received ['+str(bufSize)+'] bytes from ' + str(haspSerial.name) + ': ' + str(command))
        cmdBytes = bytes(command[2:3]) + bytes(command[3:4])
        if cmdBytes == b'\x11\x12':
            if actuatorStatus and motorStatus:  # Prevent actuator from retracting while the motor is deployed
                logging.warning('Cannot retract actuator while motor is active.')
            else:
                written = arduinoSerial.write(cmdBytes)
                logging.info('Wrote [' + str(written) + '] bytes to ' + str(arduinoSerial.name)  + ': ' + str(cmdBytes))
                if written is 2:
                    actuatorStatus = not actuatorStatus
                    if actuatorStatus:
                        logging.info('Extending actuator...')
                    else:
                        logging.info('Retracting actuator...')
                else:
                    logging.error('Action not completed!')
                arduinoSerial.flush()
        elif cmdBytes == b'\x21\x22':
            if not actuatorStatus and not motorStatus: # Prevent motor from deploying while actuator is retracted
                logging.warning('Cannot deploy motor while actuator is not extended.')
            else:
                written = arduinoSerial.write(cmdBytes)
                logging.info('Wrote ' + str(written) + ' bytes to ' + str(arduinoSerial.name) + ': ' + str(cmdBytes))
                if written is 2:
                    motorStatus = not motorStatus
                    if motorStatus:
                        logging.info('Activating motor...')
                    else:
                        logging.info('Stopping motor...')
                else:
                    logging.error('Action not completed!')
                arduinoSerial.flush()
        elif cmdBytes == b'RR':
            logging.info('Rebooting Raspberry Pi.')
            rebootPi()
    #else:
    #    logging.info('No commands found.')

# Used to test the serial connection from the Pi to the Arduino
def testSerialArduino():
    command = input('Enter command: ')
    if command is 'AA':
        logging.info('Toggling actuator.')
        arduinoSerial.write(b'AA')
        arduinoSerial.flush()
    elif command is 'MM':
        logging.info('Toggling motor')
        arduinoSerial.write(b'MM')
        arduinoSerial.flush()
    else:
        logging.warning('Command not recognized: ' + str(command))

