#!/usr/bin/python
import time
import datetime
import measure

from acquisition.acquisition_example import do_hasp_acquisition, device

file = open("num.txt", "r+")
num = int(file.read())
num += 1
file.seek(0)
file.write(str(num))
file.close()


def log_temp():
    with open("mp_temp" + str(num) + ".csv", "a") as log:
        temp = measure.get_mp_temp(device)
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d  [')  # [:%M:%S.%f')[:-3]
        ntime = datetime.datetime.fromtimestamp(ts).strftime(":%M:%S.%f")[:-3]
        hour = int(datetime.datetime.fromtimestamp(ts).strftime("%H"))
        if (hour + 5 > 23):
            new = hour - 19
        else:
            new = hour + 5
        log.write(
            "Pi: " + str(measure.get_rpi_temp()) + "  Mp:  " + str("%.3f" % measure.get_mp_temp(device)) + "  " + str(
                date) + str("{:02}").format(new) + str(ntime) + "] \n")


if __name__ == "__main__":
    while True:
        log_temp()
        print("Running acquisition now")
        do_hasp_acquisition()