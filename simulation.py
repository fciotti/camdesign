from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from utils import *
from matplotlib.patches import Circle, Wedge
import numpy as np
from shapely.geometry import LinearRing, LineString
import matplotlib.animation as animation


def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    miny, maxy = ax2.get_ylim()
    ax2.set_ylim(miny+dy, maxy+dy)


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

    velocity = np.gradient(foll_heights, edge_order=2)
    acceleration = np.gradient(velocity, edge_order=2)

    # Initialize graphics
    fig, ax = plt.subplots() # 1, 2, sharey=True)
    g = gridspec.GridSpec(2, 2)
    ax0 = plt.subplot(g[:, 0])
    ax0.axis('equal')
    # max_coord
    # max_x = max(max_coord, follower.offset + follower.radius)
    # ax0.set_xlim(-max_coord, max_x)
    ax0.set_ylim(-rho_max, np.max(foll_heights)+(follower.radius if follower.kind != 'flat' else 0))
    # ax0.margins(1)
    cam_plot, = ax0.plot(*cam.coords)
    if follower.kind == 'flat':
        # foll_plot = Rectangle((0, height), rho_max*2, 0)
        foll_plot = plt.Line2D((-rho_max, rho_max), (height, height), lw=1)
        ax0.add_line(foll_plot)
    elif follower.kind == 'knife':
        foll_plot = Wedge((follower.offset, foll_heights[0]), rho_max, 89, 91)
        ax0.add_patch(foll_plot)
    else:
        foll_plot = Circle((follower.offset, foll_heights[0]), follower.radius, fill=False)
        ax0.add_patch(foll_plot)
    ax0.plot()
    ax1 = plt.subplot(g[0, 1])
    ax1.plot(np.linspace(0, 2 * np.pi, steps), foll_heights)
    ax1.set_xlim(0, 2 * np.pi)
    ax2 = plt.subplot(g[1, 1])
    ax2.plot(np.linspace(0, 2 * np.pi, steps), velocity, 'b')
    ax2.set_ylabel('velocity', color='b')
    ax2.tick_params('y', colors='b')
    ax2.grid(True)
    ax2t = ax2.twinx()
    ax2t.plot(np.linspace(0, 2 * np.pi, steps), acceleration, 'r')
    ax2t.set_ylabel('acceleration', color='r')
    ax2t.tick_params('y', colors='r')
    ax2.set_xlim(0, 2 * np.pi)

    ax2my = max(-ax2.get_ylim()[0], ax2.get_ylim()[1])
    ax2.set_ylim(-ax2my, ax2my)
    ax2tmy = max(-ax2t.get_ylim()[0], ax2t.get_ylim()[1])
    ax2t.set_ylim(-ax2tmy, ax2tmy)
    #ax2.spines['bottom'].set_position('center')
    #ax2.spines['top'].set_color('none')
    #ax2t.spines['bottom'].set_position('center')
    #ax2t.spines['top'].set_color('none')
    #ax2.xaxis.set_ticks_position('bottom')
    #ax2.yaxis.set_ticks_position('left')
    #inv = ax2t.transData.inverted()
    # _, dy = inv.transform((0, 0)) - inv.transform((0, ax2.transData.transform((0, 0)) - ax2t.transData.transform((0, 0))))
    # d = inv - inv.transform((0, ax2.transData[1] - ax2t.transData[1]))
    #miny, maxy = ax2t.get_ylim()
    #ax2.set_ylim(miny + d[1], maxy + d[1])

    t = 2*np.pi/omega
    fps = 100
    frames = round(fps*t)
    fps_real = frames/t
    interval = 1000/fps_real
    anim = animation.FuncAnimation(fig, update, frames, interval=interval, repeat=True, blit=True,
                                   fargs=(cam_plot, foll_plot, cam_coords, foll_heights, follower.kind, steps, frames))
    plt.show()
