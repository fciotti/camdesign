from matplotlib import pyplot as plt
from utils import *
from time import time
from matplotlib.patches import Circle
import numpy as np
from shapely.geometry import LinearRing
from shapely.affinity import translate
import sys
import matplotlib.animation as animation


def update(n, cam_plot, foll_plot, cam_positions, foll_heights):
    i = int(n/120*len(foll_heights))
    cam_plot.set_data(cam_positions[i].T)
    foll_plot.center = foll_plot.center[0], foll_heights[i]
    return cam_plot, foll_plot


def draw(cam, follower, omega):
    cam_points = cartesian(cam.theta, cam.rho)
    cam_body = LinearRing(cam_points)
    height = np.max(cam.rho + follower.radius)
    if follower.kind == 'knife':
        None
    elif follower.kind == 'flat':
        None
    else:
        foll_points = cartesian(cam.theta, follower.radius)
        foll_points[:, 0] += follower.offset
        foll_points[:, 1] += height
        foll_body = LinearRing(foll_points)
    cam_positions = []
    foll_heights = []

    progress = Progress()
    for theta0 in np.linspace(0, 2*np.pi, len(cam.theta)/10):  # range is free for changes
        # dtheta = omega * 0.1 if cam.ccw else -omega * 0.1
        # theta0 += dtheta
        # TODO Flat, knife
        cam_points = cartesian(cam.theta + theta0, cam.rho)
        cam_positions.append(cam_points)
        cam_body = LinearRing(cam_points)
        if foll_body.intersects(cam_body):
            foll_body = translate(foll_body, yoff=0.01)
            height += 0.01
            while foll_body.intersects(cam_body):
                foll_body = translate(foll_body, yoff=0.01)
                height += 0.01
        else:
            foll_body = translate(foll_body, yoff=-0.01)
            height -= 0.01
            while not foll_body.intersects(cam_body):
                foll_body = translate(foll_body, yoff=-0.01)
                height -= 0.01
        foll_heights.append(height)

        # TODO calculate velocity and ...
        progress(theta0 / 2 / np.pi)
    progress.close()

    # Initialize graphics
    # plt.ion()
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.margins(1)
    cam_plot, = ax.plot(*cam_points.T)
    if follower.kind == 'knife':
        foll_plot = None
    elif follower.kind == 'flat':
        None
    else:
        foll_plot = Circle((follower.offset, height), follower.radius, fill=False)
    ax.add_patch(foll_plot)
    anim = animation.FuncAnimation(fig, update, 120, fargs=(cam_plot, foll_plot, cam_positions, foll_heights),
                                   interval=2*np.pi/omega, repeat=True)
    plt.show()
