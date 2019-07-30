#/usr/bin/env python

# This script monitors the flight computer driver script 'run.py'
# in order to ensure that the script is running.

import os
import sys
from time import sleep

dir = os.getcwd()
pidfile = "/tmp/fc.pid"

while True:
    sleep(0.1)
    if os.path.isfile(pidfile):
        print "run.py is running"
    else:
        print "run.py is not running, starting script"
        try:
            print('Starting run.py')
            sleep(1)
            os.system('python ' + dir + '/run.py &')
        except Exception as e:
            print(e)
