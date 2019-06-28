import struct
import smbus
import sys
#from settings import i2CBUS


def read_voltage(bus):
    """This function returns as float the voltage from the Raspi UPS Hat via
     the provided SMBus object"""
    address = 0x36
    read = bus.read_word_data(address, 2)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    voltage = swapped * 78.125 / 1000000
    return voltage


def read_capacity(bus):
    """This function returns as a float the remaining capacity of the battery
    connected to the Raspi UPS Hat via the provided SMBus object"""
    address = 0x36
    read = bus.read_word_data(address, 4)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped / 256
    return capacity


if __name__ == "__main__":

    bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

    print
    "Voltage:%5.2fV" % read_voltage(bus)

    print
    "Battery:%5i%%" % read_capacity(bus)

    # draw battery

    n = int(round(read_capacity(bus) / 10));

    print
    "----------- "

    sys.stdout.write('|')

    for i in range(0, n):
        sys.stdout.write('#')

    for i in range(0, 10 - n):
        sys.stdout.write(' ')

    sys.stdout.write('|+\n')

    print
    "----------- "

    if read_capacity(bus) == 100:
        print
        "Battery FULL"

    if read_capacity(bus) < 20:
        print
        "Battery LOW"
