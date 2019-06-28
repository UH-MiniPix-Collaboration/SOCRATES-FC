import pickle
import csv
import pytz

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from numpy import std, arange
from math import sqrt, degrees

from analysis.minipix import *

cluster_types = ["SMALL_BLOB", "HEAVY_TRACK", "HEAVY_BLOB", "MEDIUM_BLOB", "STRAIGHT_TRACK", "LIGHT_TRACK"]

utc = pytz.UTC


def get_cluster_count(file, data):
    for frame in range(file.num_frames):
        frame_data = data.get(frame, None)

        if frame_data:
            acq_time = data[frame]["acq_time"].replace(tzinfo=utc)
            clusters = data[frame]["clusters"]

            # Cluster types
            types = [cluster[5] for cluster in clusters]
            type_freq = {c_type: types.count(c_type) for c_type in cluster_types}

            print(acq_time, end=",")
            print(",".join(map(str, type_freq.values())))
        else:
            acq_time = file.timestamps[frame]
            print(acq_time, end=",")
            print("0,0,0,0,0,0")


def get_frame_energy(file, data):
    for frame in range(file.num_frames):
        frame_data = data.get(frame, None)

        if frame_data:
            acq_time = data[frame]["acq_time"].replace(tzinfo=utc)
            clusters = data[frame]["clusters"]
            # Total energy
            cluster_energy = [cluster[2] for cluster in clusters]
            total_energy = sum(cluster_energy)

            print(acq_time, end=",")
            print(total_energy)
        else:
            acq_time = file.timestamps[frame]
            print(acq_time, end=",")
            print(0)


def get_LET(file, data):
    for frame in range(file.num_frames):
        frame_data = data.get(frame, None)

        if frame_data:
            acq_time = data[frame]["acq_time"].replace(tzinfo=utc)
            clusters = data[frame]["clusters"]
            # Total energy
            for cluster in clusters:
                trklen = cluster[7]
                truetrkln = sqrt((55*trklen)**2 + 500**2)
                aoi = degrees(arctan(500/(55*trklen)))
                print("{},{}".format(truetrkln, aoi), end=",")
            total_energy = sum(cluster_energy)

            print(acq_time)
        else:
            acq_time = file.timestamps[frame]
            print(acq_time, end=",")
            print(0)


def get_cluster_energy(file, data):
    cluster_types = {
        "SMALL_BLOB": [],
        "HEAVY_TRACK": [],
        "HEAVY_BLOB": [],
        "MEDIUM_BLOB": [],
        "STRAIGHT_TRACK": [],
        "LIGHT_TRACK": []
    }

    for frame in range(file.num_frames):
        frame_data = data.get(frame, None)

        if frame_data:
            acq_time = data[frame]["acq_time"].replace(tzinfo=utc)
            clusters = data[frame]["clusters"]

            for cluster in clusters:
                type = cluster[5]
                energy = cluster[2]
                cluster_types[type].append((str(acq_time), type, str(energy)))

    for cluster_type in cluster_types:
        filename = cluster_type + ".csv"

        csvfile = open(filename, "w")
        csvwriter = csv.writer(csvfile)

        csvwriter.writerow(["Timestamp", "Type", "Energy"])
        for cluster in cluster_types[cluster_type]:
            csvwriter.writerow(cluster)


def get_energy_distribution(file, data):

    cluster_types = {
        "SMALL_BLOB": [],
        "HEAVY_TRACK": [],
        "HEAVY_BLOB": [],
        "MEDIUM_BLOB": [],
        "STRAIGHT_TRACK": [],
        "LIGHT_TRACK": []
    }
    for frame in range(file.num_frames):
        frame_data = data.get(frame, None)

        if frame_data:
            acq_time = data[frame]["acq_time"].replace(tzinfo=utc)
            clusters = data[frame]["clusters"]

            for cluster in clusters:
                type = cluster[5]
                energy = cluster[2]
                cluster_types[type].append((str(acq_time), type, str(energy)))
    """
    for cluster_type in cluster_types:
        filename = cluster_type + "_dist" + ".csv"

        csvfile = open(filename, "w")
        csvwriter = csv.writer(csvfile)

        energy = [float(cluster[2]) for cluster in cluster_types[cluster_type]]
        energy_distribution = normalized_distribution(energy, 50)

        csvwriter.writerow(["Range", "Count"])
        for r in energy_distribution:
            csvwriter.writerow([r, energy_distribution[r]])
    """
    fig, ax = plt.subplots()
    for cluster_type in cluster_types:
        energy = [float(cluster[2]) for cluster in cluster_types[cluster_type]]

        mu = sum(energy)/len(energy)
        sigma = std(energy)
        n, bins, patches = ax.hist(energy, bins=arange(0, 10000, 5))

        y = mlab.normpdf(bins, mu, sigma)
        ax.plot(bins, y, '--')

    ax.set_xlabel('Energy')
    ax.set_ylabel('Probability Density')
    ax.set_title('Light Track Frequency Distribution')
    fig.tight_layout()
    plt.show()


def normalized_distribution(data, window):
    data.sort()
    distributed_data = {}
    range = 0

    for point in data:
        if not distributed_data.get(range, None):
            distributed_data[range] = 0

        if point < range + window:
            distributed_data[range] += 1
        else:
            range += window

    # Normalize the distribution
    total = sum(distributed_data.values())
    for key in distributed_data:
        distributed_data[key] /= total

    return distributed_data

if __name__ == "__main__":
    serialized = open('clusters.pkl', 'rb')

    data = pickle.load(serialized)

    pmffile = PmfFile("HASPDATA/thurs_test36.pmf")
    pmffile.load_dsc()

    get_cluster_count(pmffile, data)
    # get_energy_distribution(pmffile, data)
    #get_cluster_energy(file, data)
    # get_cluster_count(file, data)
    # get_energy(file, data)
