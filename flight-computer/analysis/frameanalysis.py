from numpy import array, zeros, where, nonzero, transpose
from math import sqrt
from skimage.measure import label

from analysis.boundingrect import qhull2d, min_bounding_rect

MINIPIX_HEIGHT = 256
MINIPIX_WIDTH = 256


class Calibration:
    def __init__(self):
        self.a = None
        self.b = None
        self.c = None
        self.t = None

    def apply_calibration(self, frame):

        e_frame = zeros(65536, dtype="float32")
        hit = nonzero(frame)

        for y in hit[0]:
            tot = frame[y]
            energy = 0
            A = self.a[y]
            T = self.t[y]
            B = self.b[y] - A * T - tot
            C = T * frame[y] - self.b[y] * T - self.c[y]

            if A != 0 and (B * B - 4.0 * A * C) >= 0:
                energy = ((B * -1) + sqrt(B * B - 4.0 * A * C)) / 2.0 / A
                if energy < 0:
                    energy = 0

            e_frame[y] = energy
        return e_frame

    def load_file(self, fobj):
        return [list(map(float, line.split())) for line in fobj.readlines()]

    def load_calib_a(self, filename):
        with open(filename, 'r') as a:
            file_a = self.load_file(a)
            self.a = array(file_a).flatten()

    def load_calib_b(self, filename):
        with open(filename, 'r') as b:
            file_b = self.load_file(b)
            self.b = array(file_b).flatten()

    def load_calib_c(self, filename):
        with open(filename, 'r') as c:
            file_c = self.load_file(c)
            self.c = array(file_c).flatten()

    def load_calib_t(self, filename):
        with open(filename, 'r') as t:
            file_t = self.load_file(t)
            self.t = array(file_t).flatten()


class Frame:
    def __init__(self, framedata):
        self.cluster_count = 0
        self.clusters = []
        self.acq_time = None
        self.framedata = framedata
        self.data_array = None

    def do_clustering(self):
        arr = self.framedata.reshape(256, 256)
        binarr = array(self.framedata.reshape(256, 256))
        binarr[arr > 0] = 1
        marked, counts = label(binarr, connectivity=2, neighbors=8, return_num=True)
        self.cluster_count = counts

        hit_pixels = transpose(nonzero(marked))

        clusters = {}

        for x, y in hit_pixels:
            if marked[x][y] not in clusters.keys():
                clusters[marked[x][y]] = [(x, y, arr[x][y])]
            else:
                clusters[marked[x][y]].append((x, y, arr[x][y]))

        for cluster in clusters:
            self.clusters.append(Cluster(clusters[cluster]))


class Cluster:
    def __init__(self, indices):
        self.indices = indices

        self.bounding_rect = BoundingBox(indices)
        self.pixel_count = len(indices)
        if not (self.bounding_rect.height == 0 or self.bounding_rect.width == 0):
            self.lw_ratio = self.bounding_rect.height / self.bounding_rect.width
            self.density = self.pixel_count / self.bounding_rect.area
        else:
            self.lw_ratio = 1
            self.density = 1

        self.energy = sum([index[2] for index in indices])
        self.track_length = self._get_track_length()
        # self.LET = self.energy / self.track_length

    def _get_track_length(self):
        return None

    def _get_inner_pixels(self):
        return len(
            list(
                filter(lambda x: self._is_inner_pixel(x), self.indices)))

    def _is_inner_pixel(self, pixel):
        points = [(x[0], x[1]) for x in self.indices]

        x, y, _ = pixel

        count = 0

        if (x, y - 1) in points:
            count += 1
        if (x, y + 1) in points:
            count += 1
        if (x - 1, y) in points:
            count += 1
        if (x + 1, y) in points:
            count += 1
        if (x - 1, y + 1) in points:
            count += 1
        if (x + 1, y + 1) in points:
            count += 1
        if (x - 1, y - 1) in points:
            count += 1
        if (x + 1, y - 1) in points:
            count += 1

        return count > 4


class BoundingBox:
    def __init__(self, pixels):
        self.rotation = None
        self.area = None
        self.width = None
        self.height = None
        self.center = None
        self.corners = None
        self.pixels = array([(x[0], x[1]) for x in pixels])
        self._calculate()

    def _calculate(self):
        hull = qhull2d(array(self.pixels))
        hull = hull[::-1]
        self.rotation, self.area, self.width, self.height, self.center, self.corners = min_bounding_rect(hull)
