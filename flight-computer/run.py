#!/usr/bin/python

import os
os.environ['LD_LIBRARY_PATH'] = os.getcwd()

import smbus
import pypixet
import logging

from datetime import datetime
from numpy import array, nonzero
from numpy import sum as npsum
from picamera import PiCamera
from time import sleep, strftime

from settings import i2CBUS
from acquisition.minipixacquisition import MiniPIXAcquisition, take_acquisition
from analysis.frameanalysis import Frame, Calibration
from cmdprocessing.processcmd import HASPCommandHandler, SerialConnectionTest
from serialconnections.serialconnections import connectToHASP, connectToArduino, packetHandler, downlinkPacket
from datalogging.dataBaseStorage import measure_pi_temp, storeDataInDatabase
from datalogging.logPWMSweep import checkPWMTime, storeInCSVFiles

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(name)-8s %(levelname)-8s %(message)s',
                    filename='log.txt',
                    filemode='w')

logger = logging.getLogger('fli_comp')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
sle = logging.StreamHandler()
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)                    

time_fmt = '%Y-%m-%d-%H:%M:%S'

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
            mp_acq, mp_count = self.minipix.get_last_acquisition(block=True)
            mp_arr = array(mp_acq) 
            mp_energy = self.calibration.apply_calibration(mp_arr)
                
            mp_frame = Frame(array(mp_energy))
            if mp_count > 0:
                mp_frame.do_clustering()
            mp_total_energy = npsum(mp_energy[nonzero(mp_energy)]) 
            mp_dose = (mp_total_energy/96081.3)/self.minipix.shutter_time
            logger.info("MP Pixel Count: {} MP Clusters: {} MP Total Energy: {:.5f} MP DoseRate: {}".format(mp_count, mp_frame.cluster_count, mp_total_energy, mp_dose*60))

            mp_cluster_counts = 0
            for i, mp_cluster in enumerate(mp_frame.clusters):
                logger.info("\tCluster: {} Density: {:.2f} Energy: {:.5f}".format(i, mp_cluster.density, mp_cluster.energy))
                mp_cluster_counts = i+1

            if packet is not None:
                if packet.find('begin_pwm') is not -1:
                    storeInCSVFiles(packet)  # Send IV packet to CSV
                else:
                    # Handle case when there are multiple packets grouped together
                    packet_arr = packet.split('\n')
                    packet_arr.pop(-1)
                    logger.debug('packet_arr: ' + str(packet_arr))
                    for i, packet_from_array in enumerate(packet_arr):
                        if i > 0:
                            mp_dose = 0
                            mp_cluster_counts = 0 
                        mp2_data = str(self.get_device_temp())+','+str(mp_dose)+','+str(mp_cluster_counts)
                        packet_from_array = packet_from_array[:packet_from_array.find(',')] + ',' + mp2_data + packet_from_array[packet_from_array.find(','):]
                        mp1_data = str(self.get_device_temp())+','+str(mp_dose)+','+str(mp_cluster_counts)
                        packet_from_array = packet_from_array[:packet_from_array.find(',')] + ',' + mp1_data + packet_from_array[packet_from_array.find(','):]
                        packet_from_array = packet_from_array[:packet_from_array.find(',')] + ',' + measure_pi_temp() + packet_from_array[packet_from_array.find(','):]
                        packet_from_array = packet_from_array[:packet_from_array.find('\r')] + ',' + str(datetime.now().strftime(time_fmt))
                        storeDataInDatabase(packet_from_array)
                        downlinkPacket(self.hasp_serial_connection, packet_from_array + '\n')


            
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
