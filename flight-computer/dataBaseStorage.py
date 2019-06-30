import serial
import time
import datetime
import os
import mysql.connector as mariadb
import array
import struct as struct
import logging
from struct import *

def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline().strip('\n')
    return (temp.replace("temp=","").replace("\'C",""))

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

def storeDataInDatabase():
    dataString = readArduinoData()
    print(dataString)
    dataArray = removeCommasFromString(dataString)
    print(dataArray)
    raspberryPiTemperature = measurePiTemp()
    #Connects to the mysql database 
    mariadb_connection = mariadb.connect(
        host = "localhost",
        user = "user",
        passwd = "password",
        database = "tempdb"
        )
    cursor = mariadb_connection.cursor()
    sql = "INSERT INTO socratesTable (packet_num, RPI_temp, minipix0_temp, minipix0_dose, minipix0_counts , minipix1_temp, minipix1_dose, minipix0_counts, ambient_pressure, ISS_pressure, ISS_temp, solar_cell_temps, photodiodes) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = ("  ",raspberryTemperature,dataArray[0]," "," "," ", " ", " ", " ", " ", " ", " ", " ")
    #storeDataInTxtFiles(" ", raspberryTemperature, " ", " ", " ", " ", " ", " ", " ")
    #Inserts the values from 'val' into their respective columns in 'sql'
    cursor.execute(sql, val)
    mariadb_connection.commit()
    mariadb_connection.close()