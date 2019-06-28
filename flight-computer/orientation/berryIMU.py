#!/usr/bin/python
#
#	This program  reads the angles from the acceleromter, gyrscope
#	and mangnetometeron a BerryIMU connected to a Raspberry Pi.
#
#	This program includes two filters (low pass and mdeian) to improve the 
#	values returned from BerryIMU by reducing noise.
#
#
#	http://ozzmaker.com/
#
#    Copyright (C) 2017  Mark Williams
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Library General Public
#    License as published by the Free Software Foundation; either
#    version 2 of the License, or (at your option) any later version.
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    Library General Public License for more details.
#    You should have received a copy of the GNU Library General Public
#    License along with this library; if not, write to the Free
#    Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
#    MA 02111-1307, USA


import smbus
import time
import math
import datetime

from orientation.LSM9DS0 import *
from settings import i2CBUS

bus = smbus.SMBus(i2CBUS)

IMU_upside_down = 0 	# Change calculations depending on IMu orientation. 
						# 0 = Correct side up. This is when the skull logo is facing down
						# 1 = Upside down. This is when the skull logo is facing up 
						
						
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  	# [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      	# Complementary filter constant
MAG_LPF_FACTOR = 0.4 	# Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4 	# Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9    	# Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9    	# Median filter table size for magnetometer. Higher = smoother but a longer delay

#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0



def kalmanFilterY ( accAngle, gyroRate, DT):
	y=0.0
	S=0.0

	global KFangleY
	global Q_angle
	global Q_gyro
	global y_bias
	global YP_00
	global YP_01
	global YP_10
	global YP_11

	KFangleY = KFangleY + DT * (gyroRate - y_bias)

	YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
	YP_01 = YP_01 + ( - DT * YP_11 )
	YP_10 = YP_10 + ( - DT * YP_11 )
	YP_11 = YP_11 + ( + Q_gyro * DT )

	y = accAngle - KFangleY
	S = YP_00 + R_angle
	K_0 = YP_00 / S
	K_1 = YP_10 / S
	
	KFangleY = KFangleY + ( K_0 * y )
	y_bias = y_bias + ( K_1 * y )
	
	YP_00 = YP_00 - ( K_0 * YP_00 )
	YP_01 = YP_01 - ( K_0 * YP_01 )
	YP_10 = YP_10 - ( K_1 * YP_00 )
	YP_11 = YP_11 - ( K_1 * YP_01 )
	
	return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
	x=0.0
	S=0.0

	global KFangleX
	global Q_angle
	global Q_gyro
	global x_bias
	global XP_00
	global XP_01
	global XP_10
	global XP_11


	KFangleX = KFangleX + DT * (gyroRate - x_bias)

	XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
	XP_01 = XP_01 + ( - DT * XP_11 )
	XP_10 = XP_10 + ( - DT * XP_11 )
	XP_11 = XP_11 + ( + Q_gyro * DT )

	x = accAngle - KFangleX
	S = XP_00 + R_angle
	K_0 = XP_00 / S
	K_1 = XP_10 / S
	
	KFangleX = KFangleX + ( K_0 * x )
	x_bias = x_bias + ( K_1 * x )
	
	XP_00 = XP_00 - ( K_0 * XP_00 )
	XP_01 = XP_01 - ( K_0 * XP_01 )
	XP_10 = XP_10 - ( K_1 * XP_00 )
	XP_11 = XP_11 - ( K_1 * XP_01 )
	
	return KFangleX

def writeACC(register,value):
        bus.write_byte_data(ACC_ADDRESS , register, value)
        return -1

def writeMAG(register,value):
        bus.write_byte_data(MAG_ADDRESS, register, value)
        return -1

def writeGRY(register,value):
        bus.write_byte_data(GYR_ADDRESS, register, value)
        return -1



def readACCx():
        acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
        acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCy():
        acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
        acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCz():
        acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
        acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readMAGx():
        mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_X_L_M)
        mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_X_H_M)
        mag_combined = (mag_l | mag_h <<8)

        return mag_combined  if mag_combined < 32768 else mag_combined - 65536


def readMAGy():
        mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Y_L_M)
        mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Y_H_M)
        mag_combined = (mag_l | mag_h <<8)

        return mag_combined  if mag_combined < 32768 else mag_combined - 65536


def readMAGz():
        mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Z_L_M)
        mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Z_H_M)
        mag_combined = (mag_l | mag_h <<8)

        return mag_combined  if mag_combined < 32768 else mag_combined - 65536



def readGYRx():
        gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_X_L_G)
        gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_X_H_G)
        gyr_combined = (gyr_l | gyr_h <<8)

        return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536
  

def readGYRy():
        gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Y_L_G)
        gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Y_H_G)
        gyr_combined = (gyr_l | gyr_h <<8)

        return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

def readGYRz():
        gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Z_L_G)
        gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Z_H_G)
        gyr_combined = (gyr_l | gyr_h <<8)

        return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536



	
#initialise the accelerometer
writeACC(CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
writeACC(CTRL_REG2_XM, 0b00100000) #+/- 16G full scale

#initialise the magnetometer
writeMAG(CTRL_REG5_XM, 0b11110000) #Temp enable, M data rate = 50Hz
writeMAG(CTRL_REG6_XM, 0b01100000) #+/-12gauss
writeMAG(CTRL_REG7_XM, 0b00000000) #Continuous-conversion mode

#initialise the gyroscope
writeGRY(CTRL_REG1_G, 0b00001111) #Normal power mode, all axes enabled
writeGRY(CTRL_REG4_G, 0b00110000) #Continuos update, 2000 dps full scale

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
CFangleXFiltered = 0.0
CFangleYFiltered = 0.0
kalmanX = 0.0
kalmanY = 0.0
oldXMagRawValue = 0
oldYMagRawValue = 0
oldZMagRawValue = 0
oldXAccRawValue = 0
oldYAccRawValue = 0
oldZAccRawValue = 0
	
a = datetime.datetime.now()



#Setup the tables for the mdeian filter. Fill them all with '1' soe we dont get device by zero error 
acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
mag_medianTable1X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE




while True:
	
	
	#Read the accelerometer,gyroscope and magnetometer values
	ACCx = readACCx()
	ACCy = readACCy()
	ACCz = readACCz()
	GYRx = readGYRx()
	GYRy = readGYRy()
	GYRz = readGYRz()
	MAGx = readMAGx()
	MAGy = readMAGy()
	MAGz = readMAGz()
	
	##Calculate loop Period(LP). How long between Gyro Reads
	b = datetime.datetime.now() - a
	a = datetime.datetime.now()
	LP = b.microseconds/(1000000*1.0)
	print "Loop Time | %5.2f|" % ( LP ),
	
	
	
	############################################### 
	#### Apply low pass filter ####
	###############################################
	MAGx =  MAGx  * MAG_LPF_FACTOR + oldXMagRawValue*(1 - MAG_LPF_FACTOR);
	MAGy =  MAGy  * MAG_LPF_FACTOR + oldYMagRawValue*(1 - MAG_LPF_FACTOR);
	MAGz =  MAGz  * MAG_LPF_FACTOR + oldZMagRawValue*(1 - MAG_LPF_FACTOR);
	ACCx =  ACCx  * ACC_LPF_FACTOR + oldXAccRawValue*(1 - ACC_LPF_FACTOR);
	ACCy =  ACCy  * ACC_LPF_FACTOR + oldYAccRawValue*(1 - ACC_LPF_FACTOR);
	ACCz =  ACCz  * ACC_LPF_FACTOR + oldZAccRawValue*(1 - ACC_LPF_FACTOR);
	
	oldXMagRawValue = MAGx
	oldYMagRawValue = MAGy
	oldZMagRawValue = MAGz
	oldXAccRawValue = ACCx
	oldYAccRawValue = ACCy
	oldZAccRawValue = ACCz
	
	
	
	
	######################################### 
	#### Median filter for accelerometer ####
	#########################################
	# cycle the table
	for x in range (ACC_MEDIANTABLESIZE-1,0,-1 ):
		acc_medianTable1X[x] = acc_medianTable1X[x-1]
		acc_medianTable1Y[x] = acc_medianTable1Y[x-1]
		acc_medianTable1Z[x] = acc_medianTable1Z[x-1]
		
	# Insert the lates values	
	acc_medianTable1X[0] = ACCx
	acc_medianTable1Y[0] = ACCy
	acc_medianTable1Z[0] = ACCz	
	
	# Copy the tables
	acc_medianTable2X = acc_medianTable1X[:]
	acc_medianTable2Y = acc_medianTable1Y[:]
	acc_medianTable2Z = acc_medianTable1Z[:]
		
	# Sort table 2
	acc_medianTable2X.sort()
	acc_medianTable2Y.sort()
	acc_medianTable2Z.sort()

	# The middle value is the value we are interested in
	ACCx = acc_medianTable2X[ACC_MEDIANTABLESIZE/2];
	ACCy = acc_medianTable2Y[ACC_MEDIANTABLESIZE/2];
	ACCz = acc_medianTable2Z[ACC_MEDIANTABLESIZE/2];


	
	
	######################################### 
	#### Median filter for magnetometer ####
	#########################################
	# cycle the table
	for x in range (MAG_MEDIANTABLESIZE-1,0,-1 ):
		mag_medianTable1X[x] = mag_medianTable1X[x-1]
		mag_medianTable1Y[x] = mag_medianTable1Y[x-1]
		mag_medianTable1Z[x] = mag_medianTable1Z[x-1]
		
	# Insert the lates values	
	mag_medianTable1X[0] = MAGx
	mag_medianTable1Y[0] = MAGy
	mag_medianTable1Z[0] = MAGz	
	
	# Copy the tables
	mag_medianTable2X = mag_medianTable1X[:]
	mag_medianTable2Y = mag_medianTable1Y[:]
	mag_medianTable2Z = mag_medianTable1Z[:]
		
	# Sort table 2
	mag_medianTable2X.sort()
	mag_medianTable2Y.sort()
	mag_medianTable2Z.sort()

	# The middle value is the value we are interested in
	MAGx = mag_medianTable2X[MAG_MEDIANTABLESIZE/2];
	MAGy = mag_medianTable2Y[MAG_MEDIANTABLESIZE/2];
	MAGz = mag_medianTable2Z[MAG_MEDIANTABLESIZE/2];


	
	#Convert Gyro raw to degrees per second
	rate_gyr_x =  GYRx * G_GAIN
	rate_gyr_y =  GYRy * G_GAIN
	rate_gyr_z =  GYRz * G_GAIN


	#Calculate the angles from the gyro. 
	gyroXangle+=rate_gyr_x*LP
	gyroYangle+=rate_gyr_y*LP
	gyroZangle+=rate_gyr_z*LP


	##Convert Accelerometer values to degrees
	AccXangle =  (math.atan2(ACCy,ACCz)+M_PI)*RAD_TO_DEG
	AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG
	
	
	
		
	

	# Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up
	# Two different pieces of code are used depending on how your IMU is mounted
	if IMU_upside_down : 		# If IMU is upside down E.g Skull logo is facing up.
		if AccXangle >180:
			AccXangle -= 360.0
			AccYangle-=90
		if AccYangle >180:
			AccYangle -= 360.0

	else : 						# If IMU is up the correct way E.g Skull logo is facing down.
		AccXangle -= 180.0
		if AccYangle > 90:
			AccYangle -= 270.0
		else:
			AccYangle += 90.0



	#Complementary filter used to combine the accelerometer and gyro values.
	CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
	CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle
	
	#Kalman filter used to combine the accelerometer and gyro values.
	kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
	kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)
	
	
	
	if IMU_upside_down : 
		MAGy = -MAGy
	
	#Calculate heading
	heading = 180 * math.atan2(MAGy,MAGx)/M_PI

	#Only have our heading between 0 and 360
	if heading < 0:
	 	heading += 360



	
	#Normalize accelerometer raw values.
	accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
	accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
	
	
	#Calculate pitch and roll
	if IMU_upside_down :
		accXnorm = -accXnorm				#flip Xnorm as the IMU is upside down
		accYnorm = -accYnorm				#flip Ynorm as the IMU is upside down
		pitch = math.asin(accXnorm)
		roll = math.asin(accYnorm/math.cos(pitch))
	else :
		pitch = math.asin(accXnorm)
		roll = -math.asin(accYnorm/math.cos(pitch))


	#Calculate the new tilt compensated values
	magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
	magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

	#Calculate tilt compensated heading
	tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
	
	#Only have our heading between 0 and 360
	if tiltCompensatedHeading < 0:
		tiltCompensatedHeading += 360





	if 1:			#Change to '0' to stop showing the angles from the accelerometer
 		print ("\033[1;34;40mACCX Angle %5.2f ACCY Angle %5.2f  \033[0m  " % (AccXangle, AccYangle)),
	
	if 1:			#Change to '0' to stop  showing the angles from the gyro
		print ("\033[1;31;40m\tGRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f" % (gyroXangle,gyroYangle,gyroZangle)),

 	if 1:			#Change to '0' to stop  showing the angles from the complementary filter
		print ("\033[1;35;40m   \tCFangleX Angle %5.2f \033[1;36;40m  CFangleY Angle %5.2f \33[1;32;40m" % (CFangleX,CFangleY)),
		
 	if 1:			#Change to '0' to stop  showing the heading
		print ("HEADING  %5.2f \33[1;37;40m tiltCompensatedHeading %5.2f" % (heading,tiltCompensatedHeading)),
		
	if 1:			#Change to '0' to stop  showing the angles from the Kalman filter
		print ("\033[1;31;40m kalmanX %5.2f  \033[1;35;40m kalmanY %5.2f  " % (kalmanX,kalmanY)),

	print(" ")
	
	#slow program down a bit, makes the output more readable
	time.sleep(0.03)



	
	


		
	

	
	
	
	
	

