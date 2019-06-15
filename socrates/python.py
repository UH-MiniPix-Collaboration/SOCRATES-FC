    
import serial
import time
import datetime
import os
import mysql.connector as mariadb
import array
import struct as struct
import logging
from struct import *

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


#Function for measuring the core temp of the rasppi in farenheit
def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline().strip('\n')
    return (temp.replace("temp=","").replace("\'C",""))

def measurePiTemp():
        temp = os.popen("vcgencmd measure_temp").readline()
        temperature = temp.replace("temp=","")
        temperature = float(temperature[:-3])*1.8+32
        temperature = str(temperature)
        return temperature

#Receives and stores the arduino data in the string "arduinoData", the string includes commas
def readArduinoData():
    
    data = arduinoSerial.read(400)
    print(data)
    booleanValue = 0
    arduinoData = ""
    counter = 0
    for x in range(200,400):
        if data[x] == "[":
             for y in range(x+1, 400):
                 
                if data[y] == "]":
                   booleanValue = 1
                   break
                
                arduinoData = arduinoData+data[y]
             if booleanValue == 1:
                 break
    return arduinoData



#Removes commas and stores data in variables to be uploaded to the database
def removeCommasFromString(dataString):
    tempString = ""
    dataList = []
    for character in dataString:
        if(character == ","):
           dataList.append(tempString)
           tempString = ""
           continue
        tempString = tempString + character
    return dataList
      
    
#Stores the same data that is being sent to the database in txt files(backup)
#Also sets the name of the file to the current UTC time
def storeDataInTxtFiles(start_packet, RPI_temp, minipix1_temp, minipix2_temp,ISS_temp, ISS_pressure, ambient_pressure, solar_cells, end_packet):
    UTCTimeString = str(datetime.datetime.now()+ ".txt")
    f=open(UTCTimeString,"w+")
    #Writes to the newly ceated txt file
    f.write(start_packet + "|" + RPI_temp + "|" + minipix1_temp + "|" + minipix2_temp + "|" + ISS_temp + "|" + ISS_pressure + "|" + ambient_pressure + "|" + solar_cells + "|" + end_packet)



if __name__ == '__main__':
    try:
        connectToHASP()
        connectToArduino()
        while True:
            if haspSerial is not None and arduinoSerial is not None:
                processCommands()
                #testSerialArduino()
                readArduinoData()
                time.sleep(0.5)
        +    else:
                if haspSerial is None and arduinoSerial is None:
                    raise Exception('Missing serial connection to HASP and Arduino.')
                elif haspSerial is None:
                    raise Exception('Missing serial connection to HASP.')
                elif arduinoSerial is None:
                    raise Exception('Missing serial connection to Arduino.')
    except Exception as e:
        logging.error(e)


dataString = readArduinoData()
#dataList = removeCommasFromString(dataString)
print("dataString")
print(dataString)
dataList = removeCommasFromString(dataString)

print(dataList)
raspberryTemperature = measurePiTemp()

#Connects to the mysql database 
mariadb_connection = mariadb.connect(
    host = "localhost",
    user = "user",
    passwd = "password",
    database = "tempdb"
    )
cursor = mariadb_connection.cursor()

sql = "INSERT INTO socratesTable (start_packet, RPI_temp, minipix1_temp, minipix2_temp, ISS_temp, ISS_pressure, ambient_pressure, solar_cells, end_packet) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)"
val = ("  ",raspberryTemperature,dataList[0]," "," "," ", " ", " ", " ")

#storeDataInTxtFiles(" ", raspberryTemperature, " ", " ", " ", " ", " ", " ", " ")

#Inserts the values from 'val' into their respective columns in 'sql'
cursor.execute(sql, val)


mariadb_connection.commit()

mariadb_connection.close()