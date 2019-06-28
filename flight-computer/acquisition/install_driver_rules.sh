#!/bin/bash

# Install script for Linux distributions
# This is a basic installer that merely copies the include files and
# libraries to the system-wide directories.

# Copy the udev rules file and reload all rules
cp ./60-pixet.rules /etc/udev/rules.d
/sbin/udevadm control --reload-rules



