from threading import Thread, Event
from multiprocessing import Queue

import logging
import binascii

from time import sleep

logger = logging.getLogger('cmd_proc')
formatter = logging.Formatter('[%(asctime)s] %(name)-8s: %(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

HASP_SOH = b'\x01'
HASP_STX = b'\x02'
HASP_CMD_BYTE1 = b'\x10'
HASP_CMD_BYTE2 = b'\x20'
HASP_ETX = b'\x03'
HASP_CR = b'\x0D'
HASP_LF = b'\x0A'
HASP_CMD_COMPLETE = '\x30'

ASTROBIO_ON_BYTE1 = b'\x11'
ASTROBIO_ON_BYTE2 = b'\x12'
ASTROBIO_OFF_BYTE1 = b'\x21'
ASTROBIO_OFF_BYTE2 = b'\x22'
SOCRATES_REBOOT_BYTE1 = b'\x31'
SOCRATES_REBOOT_BYTE2 = b'\x32'


class SerialConnectionTest:
    """
    Simulates HASP commands being sent on repeat
    """
    command = [HASP_SOH,
               HASP_STX,
               b'\x41',
               b'\x42',
               HASP_ETX,
               HASP_CR,
               HASP_LF]
    cmd_index = 0

    def isOpen(self):
        return True

    def write(self, x):
        return 1

    def open(self):
        pass

    def read(self, n):
        sleep(.2)
        val = self.command[self.cmd_index]
        self.cmd_index = (self.cmd_index + 1) % len(self.command)
        return val


class HASPCommandHandler(Thread):
    def __init__(self, hasp_serial_conn, arduino_serial_conn):
        Thread.__init__(self)
        self.hasp_conn = hasp_serial_conn
        self.arduino_conn = arduino_serial_conn
        self.queue = Queue()
        self.shutdown_flag = Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            cmd = self.processcmd()
            self.arduino_conn.write(cmd)
            
    def processcmd(self):
        command_processed = False
        state = HASP_SOH
        cmd1 = None
        cmd2 = None

        while not command_processed and not self.shutdown_flag.is_set():
            in_byte = self.hasp_conn.read(1)
            logger.debug("Received byte: {}".format(binascii.hexlify(in_byte)))

            if state == HASP_SOH:
                if in_byte == b'\x01':
                    logger.info("Begin HASP Transmission")
                    state = HASP_STX
            elif state == HASP_STX:
                if in_byte == b'\x02':
                    state = HASP_CMD_BYTE1
                else:
                    state = HASP_SOH
            elif state == HASP_CMD_BYTE1:
                cmd1 = in_byte
                state = HASP_CMD_BYTE2
            elif state == HASP_CMD_BYTE2:
                cmd2 = in_byte
                state = HASP_ETX
            elif state == HASP_ETX:
                if in_byte == b'\x03':
                    state = HASP_CR
                else:
                    state = HASP_SOH
            elif state == HASP_CR:
                if in_byte == b'\x0D':
                    state = HASP_LF
                else:
                    state = HASP_SOH
            elif state == HASP_LF:
                if in_byte == b'\x0A':
                    state = HASP_CMD_COMPLETE
                    command_processed = True
                else:
                    state = HASP_SOH
            else:
                state = HASP_SOH

        logger.info("End HASP Transmission")

        return cmd1, cmd2


if __name__ == "__main__":
    test_serial = SerialConnectionTest()

    cmdHandler = HASPCommandHandler(test_serial)
    logger.info("Starting HASP command handler")
    cmdHandler.start()
    # Accept 3 uplink commands
    for i in range(3):
        cmd1, cmd2 = cmdHandler.queue.get()
        print("Received CMD1: {0} CMD2: {1}".format(binascii.hexlify(cmd1), binascii.hexlify(cmd2)))
    logger.info("Sending shutdown command")
    cmdHandler.shutdown_flag.set()
    cmdHandler.join()
