from matplotlib import pyplot as plt
from utils import *
from matplotlib.patches import Circle, Wedge
import numpy as np
from shapely.geometry import LinearRing, LineString
import matplotlib.animation as animation


def update(n, cam_plot, foll_plot, cam_coords, foll_heights, kind, steps, frames):
    i = int(n/frames*steps)
    cam_plot.set_data(cam_coords[i])
    if kind == 'flat':
        foll_plot.set_ydata((foll_heights[i], foll_heights[i]))
    elif kind == 'knife':
        foll_plot.set_center((foll_plot.center[0], foll_heights[i]))
    else:
        foll_plot.center = foll_plot.center[0], foll_heights[i]
    return cam_plot, foll_plot


def translate(body, yoff):
    body.coords = [(point[0], point[1] + yoff) for point in body.coords]
    # for i in range(len(body.coords.xy[1])): slooow
    #    body.coords.xy[1][i] += yoff

    # arr = body.coords.array_interface()
    # np.ndarray(shape=arr['shape'], buffer=arr['data'])[:][1] += yoff  does not work (??)


# Not bad
def draw(cam, follower, omega, steps, precision):
    print('Initializing...')
    cam_points = cartesian(cam.theta, cam.rho)
    cam_body = LinearRing(cam_points).simplify(precision)
    height = np.max(cam.rho + follower.radius)
    rho_max = cam.rho.max()
    if follower.kind == 'knife':
        foll_body = LineString([(follower.offset, -rho_max), (follower.offset, rho_max)])
    elif follower.kind == 'roller':
        dt = 2*np.arccos(1-precision/follower.radius)
        foll_points = cartesian(np.arange(0, 2*np.pi, dt), follower.radius)
        foll_points[:, 0] += follower.offset
        foll_points[:, 1] += height
        foll_body = LinearRing(foll_points)
    cam_coords = np.empty([steps, 2, len(cam.theta)])
    foll_heights = np.empty([steps])

    if follower.kind == 'roller':
        s = follower.radius / 2
    else:
        s = cam.rho.min() / 2

    progress = Progress()
    for i, theta0 in enumerate(np.linspace(0, 2*np.pi, steps)):
        cam_coords[i] = cam.rot_coords(theta0)

        if follower.kind == 'roller':
            cam_body = LinearRing(cam_coords[i].T)  # maybe a rotation could be more efficient
            if foll_body.intersects(cam_body):
                translate(foll_body, yoff=s)
                height += s
                while foll_body.intersects(cam_body):
                    translate(foll_body, yoff=s)
                    height += s
                s /= 2
                translate(foll_body, yoff=-s)
                height -= s
            else:
                translate(foll_body, yoff=-s)
                height -= s
                while not foll_body.intersects(cam_body):
                    translate(foll_body, yoff=-s)
                    height -= s
                s /= 2
                translate(foll_body, yoff=+s)
                height += s
            s /= 2

            while s >= precision:
                if not foll_body.intersects(cam_body):
                    translate(foll_body, yoff=-s)
                    height -= s
                else:
                    translate(foll_body, yoff=s)
                    height += s
                s /= 2

            foll_heights[i] = height

            if i > 0:
                diff = height - foll_heights[i-1]
                height += diff
                translate(foll_body, yoff=diff)
                s = abs(diff) if diff != 0 else precision
        elif follower.kind == 'flat':
            foll_heights[i] = max(cam_coords[i][1])
        else:
            cam_body = LinearRing(cam_coords[i].T)
            foll_heights[i] = foll_body.intersection(cam_body).bounds[3]
        # TODO calculate velocity and ...
        progress(theta0 / 2 / np.pi)
    progress.close()

    # Initialize graphics
    fig, ax = plt.subplots(1, 2, sharey=True)
    ax[0].axis('equal')
    # max_x = max(max_coord, follower.offset % 1 + follower.radius)
    # ax[0].set_xlim(-max_coord, max_x)
    ax[0].set_ylim(-rho_max, np.max(foll_heights)+(follower.radius if follower.kind != 'flat' else 0))
    ax[0].margins(1)
    cam_plot, = ax[0].plot(*cam.coords)
    if follower.kind == 'flat':
        # foll_plot = Rectangle((0, height), rho_max*2, 0)
        foll_plot = plt.Line2D((-rho_max, rho_max), (height, height), lw=rho_max/10)
        ax[0].add_line(foll_plot)
    elif follower.kind == 'knife':
        foll_plot = Wedge((follower.offset, foll_heights[0]), rho_max, 89, 91)
        ax[0].add_patch(foll_plot)
    else:
        foll_plot = Circle((follower.offset, foll_heights[0]), follower.radius, fill=False)
        ax[0].add_patch(foll_plot)
    ax[0].plot()
    ax[1].plot(np.linspace(0, 2*np.pi, steps), foll_heights)
    t = 2*np.pi/omega
    fps = 100
    frames = round(fps*t)
    fps_real = frames/t
    interval = 1000/fps_real
    anim = animation.FuncAnimation(fig, update, frames, interval=interval, repeat=True, blit=True,
                                   fargs=(cam_plot, foll_plot, cam_coords, foll_heights, follower.kind, steps, frames))
    plt.show()
