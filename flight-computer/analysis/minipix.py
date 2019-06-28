import re
import subprocess

from itertools import islice
from dateutil import parser as dateparser
from math import sqrt


# Width and height of minipix detector
DATA_FRAME_WIDTH = 256
DATA_FRAME_HEIGHT = 256


# Quick way of determining line count of a file
# Note: This is not portable to non unix like systems
def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


# Describes an individual pixel from a minipix detector
# This should be expanded upon later
class Pixel:
    def __init__(self, value, dim, indices):
        self.filled = False
        self.value = value
        self.dim_x, self.dim_y = dim
        self.x, self.y = indices

    # Return all surrounding pixels that are in bounds
    def surrounding_pixels(self):
        pixels = []

        if self._inbounds(self.x, self.y - 1):
            pixels.append((self.x, self.y - 1))
        if self._inbounds(self.x, self.y + 1):
            pixels.append((self.x, self.y + 1))
        if self._inbounds(self.x - 1, self.y):
            pixels.append((self.x - 1, self.y))
        if self._inbounds(self.x + 1, self.y):
            pixels.append((self.x + 1, self.y))
        if self._inbounds(self.x - 1, self.y + 1):
            pixels.append((self.x - 1, self.y + 1))
        if self._inbounds(self.x + 1, self.y + 1):
            pixels.append((self.x + 1, self.y + 1))
        if self._inbounds(self.x - 1, self.y - 1):
            pixels.append((self.x - 1, self.y - 1))
        if self._inbounds(self.x + 1, self.y - 1):
            pixels.append((self.x + 1, self.y - 1))

        return pixels

    def hit(self):
        return self.value > 0

    def _inbounds(self, x, y):
        if x > self.dim_x - 1 or x < 0:
            return False
        if y > self.dim_y - 1 or y < 0:
            return False

        return True


# Describes minipix acquisition file
class PmfFile:
    def __init__(self, filename):
        num_lines = file_len(filename)
        self.filename = filename
        self.num_frames = int(num_lines / DATA_FRAME_HEIGHT)

        self.timestamps = []
        self.dsc_loaded = False

        self.a = None
        self.b = None
        self.c = None
        self.t = None
        self.pmf_file = open(self.filename, "r")

    # @profile
    def get_frame_raw(self, frame):

        if frame > self.num_frames or frame < 0:
            raise IndexError("Frame index out of range")

        start = frame * DATA_FRAME_HEIGHT
        end = (frame * DATA_FRAME_HEIGHT) + DATA_FRAME_HEIGHT

        lines = islice(self.pmf_file, start, end)

        return lines

    def get_frame(self, frame):

        lines = self.get_frame_raw(frame)
        pmf_data = []

        for y, line in enumerate(lines):
            row_vals = []

            for x, row_val in enumerate(line.split()):
                row_vals.append(Pixel(int(row_val), (DATA_FRAME_WIDTH, DATA_FRAME_HEIGHT), (x, y % 256)))

            pmf_data.append(row_vals)

        return pmf_data

    @staticmethod
    def frame2nparray(frame):
        array = np.ones((DATA_FRAME_HEIGHT, DATA_FRAME_WIDTH), dtype=float)
        for i, line in enumerate(frame):
            for j, value in enumerate(line.split()):
                array[i][j] = float(value)
        return array

    def get_total_energy(self, pixels):
        total_energy = 0

        for pixel in pixels:
            energy = 0
            x, y, tot = pixel

            A = self.a[y][x]
            T = self.t[y][x]
            B = self.b[y][x] - A * T - tot
            C = T * tot - self.b[y][x] * T - self.c[y][x]

            if A != 0 and (B * B - 4.0 * A * C) >= 0:
                energy = ((B * -1) + sqrt(B * B - 4.0 * A * C)) / 2.0 / A
                if energy < 0:
                    energy = 0
            total_energy += energy

        return total_energy

    def calib_loaded(self):
        calib_data = [self.a, self.b, self.c, self.t]

        if not calib_data.all():
            raise Exception("Not all of the calibration files have been loaded, cannot generate e")

    def get_frame_e(self, frame):
        self.calib_loaded()

        ToT = self.frame2nparray(self.get_frame_raw(frame))
        a, b, c, t = self.calib_data

        return self._get_energy(ToT, a, b, c, t)

    # Generator for frames
    def frames(self):
        for i in range(self.num_frames):
            yield self.get_frame(i)

    def get_frame_timestamp(self, frame):
        if self.dsc_loaded:
            return self.timestamps[frame]
        else:
            raise Exception(".dsc file not loaded, cannot determine frame timestamp")

    def load_dsc(self, filename=None):

        if self.timestamps:
            self.timestamps = []

        if filename:
            file = filename
        else:
            file = self.filename + ".dsc"

        dsc = open(file, "r")

        # Use regex magic to parse out timestamps
        timestamp_regex = '.{3}\s+.{3}\s+\d+\s\d\d:\d\d:\d\d\.\d{6}\s\d{4}'

        for line in dsc.readlines():
            if re.match(timestamp_regex, line):
                time = dateparser.parse(line.strip())
                self.timestamps.append(time)
        self.dsc_loaded = True

    def load_calib_a(self, filename):
        with open(filename, 'r') as a:
            file_a = a.readlines()
            self.a = self.frame2nparray(file_a)

    def load_calib_b(self, filename):
        with open(filename, 'r') as b:
            file_b = b.readlines()
            self.b = self.frame2nparray(file_b)

    def load_calib_c(self, filename):
        with open(filename, 'r') as c:
            file_c = c.readlines()
            self.c = self.frame2nparray(file_c)

    def load_calib_t(self, filename):
        with open(filename, 'r') as t:
            file_t = t.readlines()
            self.t = self.frame2nparray(file_t)
