from math import sqrt
import numpy as np


def is_inner_pixel(index, arr):
    px, py, _ = index

    neighbors = arr[py][px].surrounding_pixels()
    count = 0

    for pixel in neighbors:
        x, y = pixel
        if arr[y][x].hit():
            count += 1
    return count > 4

def distance(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    z = a[2] - b[2]

    return sqrt(x ** 2 + y ** 2 + z ** 2)


def distance2d(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]

    return sqrt(x ** 2 + y ** 2)


def medioid(pixels):
    # Brute force solution, could probably use memoization here
    pixel_dict = {}

    for pixel in pixels:
        sum = 0
        for other_pixel in pixels:
            sum += distance(pixel, other_pixel)
        pixel_dict[pixel] = sum

    minimum = min(pixel_dict, key=pixel_dict.get)

    x, y, w = minimum
    return x + 1, y + 1, w


def centroid(pixels):
    cx, cy, tw = (0, 0, 0)

    for i, pixel in enumerate(pixels, 1):
        x, y, w = pixel
        cx += x * w
        cy += y * w
        tw += w

    cx /= tw
    cy /= tw
    avg_cluster_value = tw / i

    return int(cx + 1), int(cy + 1), avg_cluster_value


def get_intersection(line1, line2):
    l1 = np.insert(line1, 1, -1)
    l2 = np.insert(line2, 1, -1)
    x, y, z = np.cross(l1, l2)
    a = np.hstack([x, y]) / z
    return float(a[0]), float(a[1])


def lin_equ(l1, l2):
    a = (l2[1] - l1[1])
    b = (l2[0] - l1[0])

    m = a / b
    c = (l2[1] - m * l2[0])

    return m, c


# Checks if c exists on line segment from a to b
def is_between(a, b, c):
    s = np.array([distance2d(a, c) + distance2d(c, b)])
    d = np.array([distance2d(a, b)])
    return np.isclose(s, d)
