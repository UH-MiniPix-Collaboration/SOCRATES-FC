from numpy import array, argmin, zeros
from math import pi, ceil, sqrt

from matplotlib.pyplot import imshow
from matplotlib.image import imsave

from analysis.frameanalysis import Frame
from skimage.transform import rotate


def load_frame(filename):
    with open(filename) as frame:
        lines = frame.readlines()
        vals = [list(map(int, line.strip().split())) for line in lines]
        arr = array(vals).flatten()
        return arr


def distancefromorigin(point):
    x, y = point
    
    return sqrt(x**2 + y**2)


def min_point(points):
    return min(points, key=distancefromorigin)


def crop_cluster(frame, cluster):
    binarr = zeros(256*256).reshape(256,256)
    binarr[frame > 0] = 1
    imsave('binary.png', binarr)
    rotation = cluster.bounding_rect.rotation *(180/pi)
    rotated = rotate(binarr, rotation)
    rotated_points = rotate(cluster.bounding_rect.corners, rotation)
    imsave('rotated.png', rotated)
    xp = min_point(rotated_points)
    x, y = xp
    x = ceil(x)
    y = ceil(y)
    imsave('rotated_bbox.png', rotated)
    height, width = (cluster.bounding_rect.height, cluster.bounding_rect.width)
    cropped = rotated[x:x+ceil(width*1.2), y:y+ceil(height*1.2)]
    imsave('out.png', cropped)


def main():
    arr = load_frame("carbon4_frame100.pmf")
    imsave('frame.png', arr.reshape(256,256))
    frame = Frame(arr)
    frame.do_clustering()
    for cluster in frame.clusters:
        print(cluster.energy)
    crop_cluster(arr.reshape(256, 256), frame.clusters[1])

if __name__ == "__main__":
    main()
