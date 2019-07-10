import serial
import time
import mysql.connector as mariadb
import datetime
import os
import array
import struct as struct
import logging
from struct import *

#dataPacket = "1,1.23,3.45,4.44,6.77,4.44,3.55,7.77,4.33,6.77,4.55,4.33,6.88,3.44,1.23,1.23,1.23,1.23,1.23,1.23,1.23,1.23,1.23,1.23"

def measure_pi_temp():
    temp = os.popen("vcgencmd measure_temp").readline().strip('\n')
    return (temp.replace("temp=","").replace("\'C",""))

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
    print (dataPacketArray)
    #Connects to the mysql database
    mariadb_connection = mariadb.connect(
        host = "localhost",
        user = "userOne",
        passwd = "password",
        database = "socratesTable"
    )
    cursor = mariadb_connection.cursor()
    sql = "INSERT INTO socratesData (packet_num, RPI_temp, minipix0_temp, minipix0_dose, minipix0_counts , minipix1_temp, minipix1_dose, minipix1_counts, ambient_pressure, ISS_pressure, ISS_temp, solar_cell_temp_1, solar_cell_temp_2, solar_cell_temp_3, solar_cell_temp_4, solar_cell_temp_5, solar_cell_temp_6, solar_cell_temp_7, solar_cell_temp_8 , photodiode_1, photodiode_2, photodiode_3, photodiode_4, timestamp) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = ( dataPacketArray[0]  , dataPacketArray[1]   , dataPacketArray[2]    , dataPacketArray[3]   , dataPacketArray[4]    ,  dataPacketArray[5]   ,  dataPacketArray[6]   ,  dataPacketArray[7]   ,  dataPacketArray[8]   ,  dataPacketArray[9]   ,  dataPacketArray[10]   ,  dataPacketArray[11]   ,  dataPacketArray[12], dataPacketArray[13], dataPacketArray[14], dataPacketArray[15], dataPacketArray[16], dataPacketArray[17], dataPacketArray[18], dataPacketArray[19], dataPacketArray[20], dataPacketArray[21], dataPacketArray[22], dataPacketArray[23])
    #storeDataInTxtFiles(" ", raspberryTemperature, " ", " ", " ", " ", " ", " ", " ")
    #Inserts the values from 'val' into their respective columns in 'sql'
    cursor.execute(sql, val)
    mariadb_connection.commit()
    mariadb_connection.close()
