import argparse
import pdb
import traceback
import pickle
import itertools

from analysis.mathutils import *
from analysis.minipix import *
from analysis.boundingrect import *

SMALL_BLOB = "SMALL_BLOB"
HEAVY_TRACK = "HEAVY_TRACK"
HEAVY_BLOB = "HEAVY_BLOB"
MEDIUM_BLOB = "MEDIUM_BLOB"
STRAIGHT_TRACK = "STRAIGHT_TRACK"
LIGHT_TRACK = "LIGHT_TRACK"


# Iterative floodfill (Python doesn't optimize tail recursion)
# returns list of pixel indices and their corresponding values
def floodfill(x, y, arr, threshold=0):
    to_fill = set()
    to_fill.add((x, y))

    cluster_pixels = []

    while not len(to_fill) == 0:
        x, y = to_fill.pop()

        pixel = arr[y][x]
        pixel.filled = True

        cluster_pixels.append((x, y, pixel.value))

        for x, y in pixel.surrounding_pixels():
            if arr[y][x].value > threshold and not arr[y][x].filled:
                to_fill.add((x, y))

    return cluster_pixels


def track_length(pixels, bounding_box, dim):
    x = np.array([pixel[0] for pixel in pixels])
    y = np.array([pixel[1] for pixel in pixels])

    pairs = itertools.combinations(bounding_box, 2)
    dim = np.array(dim)

    sides = filter(lambda x:
                   np.isclose(np.array([distance2d(x[0], x[1])]), dim[0]) or np.isclose(
                       np.array([distance2d(x[0], x[1])]), dim[1]),
                   pairs)

    # Least squares fit for cluster
    A = np.vstack((x, np.ones(len(x)))).T
    lsqfit = np.linalg.lstsq(A, y)[0]

    bbox_points = [(x[0], x[1]) for x in bounding_box]
    # If we don't have four distinct points to work off of then there's not much we can do
    if len(set(bbox_points)) < 4:
        return None

    intersections = []

    # Check intersection on each side of bounding box
    for side in sides:

        p1, p2 = side
        m, c = lin_equ(p1, p2)
        lsqfit_m, lsqfit_c = lsqfit

        # If slope is undefined i.e a vertical line
        if np.isinf(m):
            x = p1[0]
            intersection = (x, lsqfit_m * x + lsqfit_c)
        else:
            intersection = get_intersection(lsqfit, (m, c))

        # Use only intersections that actually lie inside the box
        if is_between(p1, p2, intersection):
            intersections.append(intersection)

    i1 = intersections[0]
    i2 = intersections[1]

    return np.array([i1, i2])


def analyze_cluster(data, frame, pixels):
    points = [(pixel[0], pixel[1]) for pixel in pixels]

    # Calculate convex hull for cluster
    hull = qhull2d(np.array(points))
    hull = hull[::-1]

    # Calculate minimum bounding rectangle
    rot_angle, area, width, height, center, corners = min_bounding_rect(hull)

    # Centroid of the cluster
    cluster_centroid = centroid(pixels)
    # Total deposited energy for a given cluster
    total_energy = data.get_total_energy(pixels)
    # Number of inner pixels for a given cluster
    inner_pixels = len(list(filter(lambda x: is_inner_pixel(x, frame), pixels)))
    # Pixel with the maximum ToT
    max_pixel = max(pixels, key=lambda x: x[2])

    # Define length  as maximum of the two sides of the rectangle
    length = max([width, height])
    width = min([width, height])

    pixelcount = len(pixels)

    trk_len = track_length(pixels, corners, (length, width))

    # Calculating convex hull for only one pixel leads to some strange behavior,
    # so special case for when n=1
    if pixelcount > 1:
        density = pixelcount / area
        lwratio = length / width
    else:
        lwratio = pixelcount
        density = 1

    if inner_pixels == 0 and pixelcount <= 4:
        cluster_type = SMALL_BLOB
    elif inner_pixels > 6 and lwratio > 1.25 and density > 0.3:
        cluster_type = HEAVY_TRACK
    elif inner_pixels > 6 and lwratio <= 1.25 and density > 0.5:
        cluster_type = HEAVY_BLOB
    elif inner_pixels > 1 and lwratio <= 1.25 and density > 0.5:
        cluster_type = MEDIUM_BLOB
    elif inner_pixels == 0 and lwratio > 8.0:
        cluster_type = STRAIGHT_TRACK
    else:
        cluster_type = LIGHT_TRACK

    return max_pixel, density, total_energy, rot_angle, cluster_centroid, cluster_type, corners, trk_len


# Determines the number of clusters given a single frame of acquisition data
def cluster_count(data, frame, threshold=0):
    clusters = 0
    cluster_info = []

    for row in frame:
        for pixel in row:
            if pixel.value > threshold and not pixel.filled:
                cluster = floodfill(pixel.x, pixel.y, frame)
                cluster_info.append(analyze_cluster(data, frame, cluster))
                clusters += 1

    return cluster_info


def n_line_iterator(fobj,n):
    if n < 1:
       raise ValueError("Must supply a positive number of lines to read")

    out = []
    num = 0
    for line in fobj:
       if num == n:
          yield out
          num = 0
          out = []
       out.append(line)
       num += 1
    yield out


def main(args):
    data = PmfFile(args.filename)
    threshold = int(args.threshold)

    data.load_calib_a("a.txt")
    data.load_calib_b("b.txt")
    data.load_calib_c("c.txt")
    data.load_calib_t("t.txt")

    data.load_dsc()

    cluster_out = open(args.outfile, 'wb')
    frames = {}

    # print("Processing {} frames...".format(data.num_frames))

    # Loop through each frame and place calculated track parameters into a dictionary
    for i, lines in enumerate(n_line_iterator(data.pmf_file, 256)):
        print("Frame {}".format(i))
        frame = data.get_frame(lines)
        energy = 0
        for cluster in cluster_count(data, frame, threshold=threshold):
            _, _, total_energy, _, _, _, _, _ = cluster
            energy += total_energy

            if not frames.get(i, False):
                frames[i] = {"acq_time": data.get_frame_timestamp(i),
                             "clusters": []}
            frames[i]["clusters"].append(cluster)

            print(cluster)

    # Serialize the dictionary for analysis later
    pickle.dump(frames, cluster_out)
    cluster_out.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Determine the cluster count for each frame in a pmf acquisition file")
    parser.add_argument('filename', help='Pmf file to process')
    parser.add_argument('-t',
                        action='store',
                        dest='threshold',
                        default=1,
                        help='Threshold')
    parser.add_argument('-o',
                        action='store',
                        dest='outfile',
                        default='clusters.pkl',
                        help='Binary output filename, defaults to clusters.pkl')
    args = parser.parse_args()

    try:
        main(args)
    # Drop into shell on failure for postmortem debugging
    except Exception:
        _, _, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
