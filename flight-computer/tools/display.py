import pygame, sys

from analysis.clusteranalysis import cluster_count
from analysis.minipix import PmfFile

import numpy as np

arr = []

RED = (255, 10, 10)
BLU = (10, 255, 10)
GRN = (10, 10, 255)
WHITE = (255, 255, 255)

arr.append(RED)
arr.append(BLU)
arr.append(GRN)

SCREEN_X = 256
SCREEN_Y = 256
threshold = 0

pygame.init()

screen = pygame.display.set_mode((512, 512))
square = pygame.Surface((2, 2))
myfont = pygame.font.SysFont("monospace", 15)


def do_visualization(file, frame, mode='bb'):
    data = file.get_frame(frame)
    cluster_info = cluster_count(file, data)

    if mode == 'bb':
        render_frame(data, screen)
        render_bb(cluster_info, screen)
    elif mode == 'track':
        render_frame(data, screen, fill=False)
        render_track(cluster_info, screen)
    elif mode == 'type':
        render_frame(data, screen)
        render_type(cluster_info, screen)

    pygame.display.flip()

    return len(cluster_info)


def render_frame(data, screen, fill=True):
    for j in range(SCREEN_Y):
        for i in range(SCREEN_X):
            if data[j][i].value > int(sys.argv[3]):
                num = 1 if fill else 2
            else:
                num = 2
            square.fill(arr[num])
            draw_me = pygame.Rect((j + 1) * 2, (i + 1) * 2, 2, 2)
            screen.blit(square, draw_me)
    pygame.display.flip()


def render_track(cluster_info, screen):
    for cluster in cluster_info:
        if cluster[7] is not None:
            path = [np.flip(np.ceil(x), 0) for x in (cluster[7] + 1) * 2.0]
            pygame.draw.lines(screen, WHITE, False, path)


def render_bb(cluster_info, screen):
    for cluster in cluster_info:
        rect_points = [np.flip(np.ceil(x), 0) for x in (cluster[6] + 1) * 2.0]
        pygame.draw.polygon(screen, RED, rect_points, 1)


def render_type(cluster_info, screen):
    for cluster in cluster_info:
        y, x, _ = cluster[4]
        label = myfont.render(str(cluster[5]), 1, (255, 255, 0))
        screen.blit(label, ((x * 2) + 5, (y * 2) + 5))


def render_centroid(cluster_info, screen):
    for cluster in cluster_info:
        y, x, _ = cluster[4]
        pixel = pygame.Surface((2, 2))
        pixel.fill(BLU)
        draw = pygame.Rect(x * 2, y * 2, 2, 2)
        screen.blit(pixel, draw)


if __name__ == "__main__":

    done = False
    frame = int(sys.argv[2])
    file = PmfFile(sys.argv[1])
    file.load_calib_a("a.txt")
    file.load_calib_b("b.txt")
    file.load_calib_c("c.txt")
    file.load_calib_t("t.txt")
    file.load_dsc()

    clusters = do_visualization(file, frame)
    visualization_types = ['bb', 'type', 'track']

    vtype = 0

    while not done:
        time = file.get_frame_timestamp(frame)
        pygame.display.set_caption("Frame {} of {}".format(frame, file.num_frames - 1))
        frame_label = myfont.render("Clusters: {} Time: {}".format(clusters, time), 1, (255, 255, 0))

        screen.blit(frame_label, (5, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if frame > 0:
                        frame -= 1
                    clusters = do_visualization(file, frame, mode=visualization_types[vtype])
                if event.key == pygame.K_RIGHT:
                    if frame < file.num_frames - 1:
                        frame += 1
                    clusters = do_visualization(file, frame, mode=visualization_types[vtype])
                if event.key == pygame.K_UP:
                    vtype = (vtype + 1) % len(visualization_types)
                    do_visualization(file, frame, mode=visualization_types[vtype])
                if event.key == pygame.K_DOWN:
                    vtype = (vtype - 1) % len(visualization_types)
                    do_visualization(file, frame, mode=visualization_types[vtype])
