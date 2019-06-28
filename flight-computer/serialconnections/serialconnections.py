import serial
import os
import logging

# Logger setup
logger = logging.getLogger('ser_conn')
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)
                    
# Open connection with a specified port, return serial object
def connectPort(portName):
    ser = None
    try:
        ser = serial.Serial(port = portName, baudrate = 4800, parity = serial.PARITY_NONE)
        if ser != None:
            logger.info('Successfully connected to port \'' + ser.name + '\' with baudrate ' + str(ser.baudrate) + '.')
        else:
            logger.warning('Could not connect to port ' + portName + '.')
    except Exception as e:
        logger.error('Error while attempting to open serial port \'' + portName + '\'.')
        logger.error(e)
    return ser


def connectToHASP():
    logger.info('Attempting connection with HASP.')
    usbPortName = ''
    dirList = os.listdir('/dev/')
    # Find all ttyUSB devices (i.e. connection via RS232)
    for name in dirList:
        if 'USB' in name:
            usbPortName = '/dev/' + name
            logger.info('Found USB port: ' + str(usbPortName))
            break
    return connectPort(usbPortName)

    
def connectToArduino():
    logger.info('Attempting connection with Arduino.')
    acmPortName = ''
    dirList = os.listdir('/dev/')
    # Find all ttyACM devices (i.e. connection to Arduino)
    for name in dirList:
        if 'ACM' in name:
            acmPortName = '/dev/' + name
            logger.info('Found ACM port: ' + str(acmPortName))
            break
    return connectPort(acmPortName)
                                                                            
def packetHandler(arduino_serial_connection):
    remainingString = ""
    remainingBytes = ''
    packetComplete = False
    if arduino_serial_connection.in_waiting > 0:
        while not packetComplete:
            bufSize = arduino_serial_connection.in_waiting
            data = arduino_serial_connection.read(bufSize)
            packet = ""
            logger.debug('Received ['+str(bufSize)+'] bytes from ' + str(arduino_serial_connection.name) + ': \'' + str(data) + '\'')
            try:
                packet = data.decode('utf-8')
            except Exception as e:
                logger.warning(e)
            eopIndex = packet.find('\n')
            fixedData = remainingString + packet[:eopIndex]
            #logger.debug("fixedString: " + fixedData)
            if eopIndex is -1:
                remainingString = remainingString + packet
                remainingBytes = remainingBytes + data
            else:
                completePacket = remainingString + packet[:eopIndex]
                logger.debug('Complete packet: ' + completePacket)
                packetComplete = True
                remainingString = ""
                remainingBytes = b''
                return completePacket
        
def downlinkPacket(hasp_serial_connection, dataPacket):
    numBytesWritten = hasp_serial_connection.write(bytes(dataPacket))
    logger.info('Sent ['+str(numBytesWritten)+'] bytes to HASP: '+str(dataPacket))
