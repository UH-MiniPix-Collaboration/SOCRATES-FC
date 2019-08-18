#!/usr/bin/python

import os
os.environ['LD_LIBRARY_PATH'] = os.getcwd()

import sys
import smbus
import pypixet
import logging
import csv

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
                    filemode='a')

logger = logging.getLogger('fli_comp')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
sle = logging.StreamHandler()
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

time_fmt = '%Y-%m-%d-%H:%M:%S'

# Setup PID file
pid = str(os.getpid())
pidfile = "/tmp/fc.pid"

if os.path.isfile(pidfile):
    print ("%s already exists, exiting" % pidfile)
    sys.exit()
pidf = open(pidfile, 'w')
pidf.write(pid)
pidf.close()


class RPIDosimeter:
    # Initialize i2c devices, minipix, logging facilities etc.
    def __init__(self):
        # Set up MiniPIX
        self.calibration = Calibration()
        self.calibration.load_calib_a("/home/pi/SOCRATES-FC/flight-computer/calibration/a.txt")
        self.calibration.load_calib_b("/home/pi/SOCRATES-FC/flight-computer/calibration/b.txt")
        self.calibration.load_calib_c("/home/pi/SOCRATES-FC/flight-comptuer/calibration/c.txt")
        self.calibration.load_calib_t("/home/pi/SOCRATES-FC/flight-computer/calibration/t.txt")
        # Initialize miniPIX driver subsystem
        pypixet.start()
        self.pixet = pypixet.pixet
        self.device = self.pixet.devices()[0]
        print(self.pixet.devices())
        
        if self.device.fullName() != "MiniPIX H06-W0239":
            print()
            logger.error("No minipix found exiting...")
            os.unlink(pidfile)
            exit(0)
        self.device.loadConfigFromFile("/home/pi/SOCRATES-FC/flight-computer/calibration/MiniPIX-H06-W0239.xml")

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

            with open('mp_clusters.csv', mode='a+') as mp_clusters_file:
                data_writer = csv.writer(mp_clusters_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                mp_clusters_file.write("\nMP Pixel Count: {} MP Clusters: {} MP Total Energy: {:.5f} MP DoseRate: {}".format(mp_count, mp_frame.cluster_count, mp_total_energy, mp_dose*60))
            
            mp_cluster_counts = 0
            for i, mp_cluster in enumerate(mp_frame.clusters):
                logger.info("\tCluster: {} Density: {:.2f} Energy: {:.5f}".format(i, mp_cluster.density, mp_cluster.energy))
                with open('mp_clusters.csv', mode='a+') as mp_clusters_file:
                    data_writer = csv.writer(mp_clusters_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    mp_clusters_file.write("\nCluster: {} Density: {:.2f} Energy: {:.5f}".format(i, mp_cluster.density, mp_cluster.energy))
                mp_cluster_counts = i+1

            if packet is not None:
                packet_arr = packet.split('\n')
                packet_arr.pop(-1)
                logger.debug('packet_arr: ' + str(packet_arr))
                # Handle case when there are multiple packets grouped together
                for i, packet_from_array in enumerate(packet_arr):
                    if packet_from_array.find('begin_pwm') is not -1:
                        logging.info('Sending cell packet to CSV:  \'' + str(packet_from_array) + '\'')
                        storeInCSVFiles(packet_from_array + '\n')  # Send IV packet to CSV
                        i = 0
                    else:
                        #print(packet)
                        if i > 0:
                            mp_dose = 0
                            mp_cluster_counts = 0
                        # Add the RPI temp, MP data, and the timestamp
                        mp2_data = str(self.get_device_temp())+','+str(mp_dose)+','+str(mp_cluster_counts)
                        packet_from_array = packet_from_array[:packet_from_array.find(',')] + ',' + mp2_data + packet_from_array[packet_from_array.find(','):]
                        mp1_data = str(self.get_device_temp())+','+str(mp_dose)+','+str(mp_cluster_counts)
                        packet_from_array = packet_from_array[:packet_from_array.find(',')] + ',' + mp1_data + packet_from_array[packet_from_array.find(','):]
                        packet_from_array = packet_from_array[:packet_from_array.find(',')] + ',' + measure_pi_temp() + packet_from_array[packet_from_array.find(','):]
                        packet_from_array = packet_from_array[:packet_from_array.find('\r')] + ',' + str(datetime.now().strftime(time_fmt))
                        if packet_from_array.count(',') == 23:  # final check to ensure that the packet is the proper size
                            storeDataInDatabase(packet_from_array)
                            downlinkPacket(self.hasp_serial_connection, packet_from_array + '\n')



    def shutdown(self):
        print("Stopping acquisitions...")
        self.minipix.shutdown()
        self.minipix.join()
        print("Exiting main thread...")
        print("Stopping HASP command handler thread...")
        #self.cmd_handler.shutdown_flag.set()
        #self.cmd_handler.join()
        # Wait for minipix to shutdown properly
        sleep(2)

if __name__ == "__main__":
    app = RPIDosimeter()
    try:
        app.main()
    except KeyboardInterrupt:
        app.shutdown()
    except Exception as e:
        logger.error(e)
    finally:
        os.unlink(pidfile)
        logger.info('Unlinked PID file.')
