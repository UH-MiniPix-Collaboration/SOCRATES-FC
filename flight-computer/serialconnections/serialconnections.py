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

remainingString = ''
remainingBytes = ''

# Open connection with a specified port, return serial object
def connectPort(portName):
    ser = None
    connected = False
    try:
        for i,_ in enumerate(range(0, 3)):
            if connected == False:
                ser = serial.Serial(port = portName, baudrate = 4800, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, xonxoff = False, rtscts = False)
                if ser != None:
                    logger.info('Successfully connected to port \'' + ser.name + '\' with baudrate ' + str(ser.baudrate) + '.')
                    connected = True
                else:
                    logger.warning('Could not connect to port ' + portName + '. Attempt ' + str(i) + ' of 3.')
    except Exception as e:
        logger.error('Error while attempting to open serial port \'' + portName + '\'.')
        logger.error(e)
    return ser


def connectToHASP():
    logger.info('Attempting connection with HASP.')
    ttySPortName = ''
    dirList = os.listdir('/dev/')
    # Find all ttyUSB devices (i.e. connection via RS232)
    for name in dirList:
        if 'ttyS' in name:
            ttySPortName = '/dev/' + name
            logger.info('Found ttyS port: ' + str(ttySPortName))
            break
    return connectPort(ttySPortName)

    
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
    global remainingString
    global remainingBytes

    packetComplete = False
    if arduino_serial_connection.in_waiting > 0:
        while not packetComplete:
            bufSize = arduino_serial_connection.in_waiting
            data = arduino_serial_connection.read(bufSize)
            packet = ""
            if bufSize != 0:
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
                completePacket = remainingString + packet[:eopIndex+1]
                remainingString = packet[eopIndex+1:] #remainingString[remainingString.find('\r'):]
                logger.debug('Remaining string: \'' + remainingString + '\'')
                if remainingString.find('\n') is not -1 and completePacket.find('begin_pwm') is -1:
                    completePacket = completePacket + remainingString
                    remainingString = ''
                logger.debug('Complete packet: ' + completePacket)
                packetComplete = True
                remainingBytes = b''
                if completePacket.find('begin_pwm') is -1:
                    remainingCommas = completePacket.count(',') % 15
                    while remainingCommas is not 0:
                        completePacket = completePacket[:completePacket.find(',')]
                        #print(completePacket)
                        remainingCommas =  completePacket.count(',') % 15
                return completePacket
        
def downlinkPacket(hasp_serial_connection, dataPacket):
    #numBytesWritten = hasp_serial_connection.write(bytes(dataPacket))
    hasp_serial_connection.write(bytes(dataPacket))
    logger.info('Sent bytes to HASP: '+str(dataPacket.rstrip()))
