#/usr/bin/env python

# This script monitors the flight computer driver script 'run.py'
# in order to ensure that the script is running.

import os
import sys
import logging
from time import sleep


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(name)-8s %(levelname)-8s %(message)s',
                    filename='monitor-fc-log.txt',
                    filemode='a')

logger = logging.getLogger('mon_srpt')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
sle = logging.StreamHandler()
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


dir = os.getcwd()
pidfile = "/tmp/fc.pid"

while True:
    sleep(1)
    if os.path.isfile(pidfile):
        logger.info("run.py is running")
    else:
        logger.info("run.py is not running, starting script")
        try:
            logger.info('Starting run.py')
            os.system('python ' + dir + '/run.py &')
            sleep(8)  # Allow time for run.py to boot
        except Exception as e:
            logger.warning(e)
