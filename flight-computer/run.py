#!/usr/bin/python

import os
os.environ['LD_LIBRARY_PATH'] = os.getcwd()  # or whatever path you want


import smbus
import pypixet
import logging

from datetime import datetime
from numpy import array, nonzero
from numpy import sum as npsum
from picamera import PiCamera
from time import sleep, strftime

from logPWMSweep import checkPWMTime, storeInCSVFiles

from settings import i2CBUS
from acquisition.minipixacquisition import MiniPIXAcquisition, take_acquisition
from analysis.frameanalysis import Frame, Calibration
from cmdprocessing.processcmd import HASPCommandHandler, SerialConnectionTest
from serialconnections.serialconnections import connectToHASP, connectToArduino, packetHandler, downlinkPacket
from dataBaseStorage import measure_pi_temp, storeDataInDatabase

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(name)-8s %(levelname)-8s %(message)s',
                    filename='log.txt',
                    filemode='w')

logger = logging.getLogger('fli_comp')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)                    


class RPIDosimeter:
    # Initialize i2c devices, minipix, logging facilities etc.
    def __init__(self):
        # Set up MiniPIX
        self.calibration = Calibration()
        self.calibration.load_calib_a("/home/pi/Desktop/MiniPIX-RPI-Dosimeter/calibration/a.txt")
        self.calibration.load_calib_b("/home/pi/Desktop/MiniPIX-RPI-Dosimeter/calibration/b.txt")
        self.calibration.load_calib_c("/home/pi/Desktop/MiniPIX-RPI-Dosimeter/calibration/c.txt")
        self.calibration.load_calib_t("/home/pi/Desktop/MiniPIX-RPI-Dosimeter/calibration/t.txt")
        # Initialize miniPIX driver subsystem
        pypixet.start()
        self.pixet = pypixet.pixet
        self.device = self.pixet.devices()[0]

        if self.device.fullName() != "MiniPIX H06-W0239":
            print()
            logger.error("No minipix found exiting...")
            exit(0)
        self.device.loadConfigFromFile("calibration/MiniPIX-H06-W0239.xml")

        logger.info("Found device: {}".format(self.device.fullName()))

        # Allows for retrieval of MiniPIX frames at regular intervals
        self.minipix = MiniPIXAcquisition(self.device, self.pixet, variable_frate=False, shutter_time=1)
        self.minipix.daemon = True

        # Allows for regular handling of uplink commmands from HASP
        self.arduino_serial_connection = connectToArduino()
        self.hasp_serial_connection = connectToHASP()
        self.cmd_handler = HASPCommandHandler(self.hasp_serial_connection, self.arduino_serial_connection)
        self.cmd_handler.start()

        self.running = False

    def __del__(self):
        self.arduino_serial_connection.close()
        self.hasp_serial_connection.close()


    def capture_image(self):
        filename = strftime("%Y-%m-%d-%H:%M:%S")
        self.camera.capture("/home/pi/images/" + filename + ".jpg")
        sleep(2)


    def get_device_temp(self):
        pars = self.device.parameters() # get parameters object
        par = pars.get("Temperature")  # temperature parameter in Minipix device
        temp = par.getDouble()
        return temp
        
        
    def main(self):
        self.minipix.start()
        self.running = True
        
        while True:
            # If there's an acquisition available for analysis
            # Receive the downlink data from the Arduino

            # Check if PWM sweep needs to be performed. Performs sweep if necessary
            checkPWMTime(self.arduino_serial_connection)
            
            cmd = b'\x41'+b'\x42'
            numBytes = self.arduino_serial_connection.write(cmd)
            if numBytes is 2:
                logger.info('Sent ['+str(numBytes)+'] bytes to SOCRATES: ' + cmd)
            else:
                logger.warning('Failed to send downlink command to SOCRATES.')
            packet = packetHandler(self.arduino_serial_connection)
            
            acq, count = self.minipix.get_last_acquisition(block=True)
            arr = array(acq) 
            energy = self.calibration.apply_calibration(arr)
                
            frame = Frame(array(energy))
            if count > 0:
                frame.do_clustering()
            total_energy = npsum(energy[nonzero(energy)]) 
            dose = (total_energy/96081.3)/self.minipix.shutter_time
            logger.info("Pixel Count: {} Clusters: {} Total Energy: {:.5f} DoseRate: {}".format(count, frame.cluster_count, total_energy, dose*60))

            cluster_counts = 0
            for i, cluster in enumerate(frame.clusters):
                logger.info("\tCluster: {} Density: {:.2f} energy: {:.5f}".format(i, cluster.density, cluster.energy))
                cluster_counts = i+1

            if packet is not None:
                if packet.find('begin_pwm') is not -1:
                    storeInCSVFiles(packet)  # Send packet to CSV
                else:
                    mp2_temp = self.get_device_temp()
                    mp2_data = str(mp2_temp)+','+str(dose)+','+str(cluster_counts)
                    packet = packet[:packet.find(',')] + ',' + mp2_data + packet[packet.find(','):]
                    mp1_temp = self.get_device_temp()
                    mp1_data = str(mp1_temp)+','+str(dose)+','+str(cluster_counts)
                    packet = packet[:packet.find(',')] + ',' + mp1_data + packet[packet.find(','):]
                    pi_temp = measure_pi_temp()
                    packet = packet[:packet.find(',')] + ',' + pi_temp + packet[packet.find(','):]
                    packet = packet[:packet.find('\n')] + ',' + str(datetime.now())
                    storeDataInDatabase(packet)
                    downlinkPacket(self.hasp_serial_connection, packet)


            
    def shutdown(self):
        print("Stopping acquisitions...")
        self.minipix.shutdown()
        self.minipix.join()
        print("Exiting main thread...")
        print("Stopping HASP command handler thread...")
        self.cmd_handler.shutdown_flag.set()
        self.cmd_handler.join()
        # Wait for minipix to shutdown properly
        sleep(2)

if __name__ == "__main__":
    app = RPIDosimeter()
    try:
        app.main()
    except KeyboardInterrupt:
        app.shutdown()
