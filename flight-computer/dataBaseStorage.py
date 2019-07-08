import serial
import time
import mysql.connector as mariadb
import datetime
import os
import array
import struct as struct
import logging
from struct import *

"""
def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline().strip('\n')
    return (temp.replace("temp=","").replace("\'C",""))
"""

#dataPacket = "1,1.23,3.45,4.44,6.77,4.44,3.55,7.77,4.33,6.77,4.55,4.33,6.88,3.44"

def dataPacketToArray(dataPacket):
    dataPacketArray = []
    dataPacketArray = dataPacket.split(",")
    print(dataPacketArray)
    return dataPacketArray

"""
def storeDataInTxtFiles(start_packet, RPI_temp, minipix1_temp, minipix2_temp,ISS_temp, ISS_pressure, ambient_pressure, solar_cells, end_packet):
    UTCTimeString = str(datetime.datetime.now()+ ".txt")
    f=open(UTCTimeString,"w+")
    #Writes to the newly ceated txt file
    f.write(start_packet + "|" + RPI_temp + "|" + minipix1_temp + "|" + minipix2_temp + "|" + ISS_temp + "|" + ISS_pressure + "|" + ambient_pressure + "|" + solar_cells + "|" + end_packet)
"""

def storeDataInDatabase(dataPacket):
    dataPacketArray = dataPacketToArray(dataPacket)
    
    #Connects to the mysql database 
    mariadb_connection = mariadb.connect(
        host = "localhost",
        user = "user",
        passwd = "password",
        database = "tempdb"
        )
    cursor = mariadb_connection.cursor()
    sql = "INSERT INTO socratesTable (packet_num, RPI_temp, minipix0_temp, minipix0_dose, minipix0_counts , minipix1_temp, minipix1_dose, minipix1_counts, ambient_pressure, ISS_pressure, ISS_temp, solar_cell_temps, photodiodes,timestamp) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"
    val = ( dataPacketArray[0]  , dataPacketArray[1]   , dataPacketArray[2]    , dataPacketArray[3]   , dataPacketArray[4]    ,  dataPacketArray[5]   ,  dataPacketArray[6]   ,  dataPacketArray[7]   ,  dataPacketArray[8]   ,  dataPacketArray[9]   ,  dataPacketArray[10]   ,  dataPacketArray[11]   ,  dataPacketArray[12], dataPacketArray[13])
   #storeDataInTxtFiles(" ", raspberryTemperature, " ", " ", " ", " ", " ", " ", " ")
    #Inserts the values from 'val' into their respective columns in 'sql'
    cursor.execute(sql, val)
    mariadb_connection.commit()
    mariadb_connection.close()


#storeDataInDatabase(dataPacket)
