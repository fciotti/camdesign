from sympy.geometry import *
import pyclipper
from utils import *
from time import time
from numpy.linalg import solve


def line(x0, y0, theta, rho, ray=False):
    if ray:
        theta = abs(theta)
    return np.array([x0+rho*np.cos(theta), y0+rho*np.sin(theta)])


def lines(theta, rho, angle):  # may be useful defining a custom angle /= pi/2
    coords = np.empty([2, len(theta)])
    B = np.empty([len(theta), 2])
    for i in range(0, len(theta)):
         B[i] = cartesian(theta[i], rho[i])  # x2 - 0, y2 - 0
    progress = Progress()
    for i in range(0, len(theta)):
        first_r = None
        # A = np.array([[np.cos(theta[i]), -np.cos(theta[j]+np.pi/2)],
        #              [np.sin(theta[i]), -np.sin(theta[j]+np.pi/2)]])
        A = np.array([[np.cos(theta[i]), 0],
                      [np.sin(theta[i]), 0]])
        for j in range(0, len(theta)):
            A[:, 1] = -np.cos(theta[j]+np.pi/2), -np.sin(theta[j]+np.pi/2)
            r1 = solve(A, B[j])[0]
            # way slower:
            # r1 = fsolve(f, np.array([rho[i], 0]), args=(0, 0, theta[i], B[j][0], B[j][1], theta[j]+np.pi/2, True))[0]
            if np.isnan(r1) or r1 < 0:
                continue
            if first_r is None or r1 < first_r:
                first_r = r1
        coords[:, i] = theta[i], first_r
        progress(i/len(theta))
    progress.close()
    return coords

    # Slow
    # length = max(rhos)*100  # Dirty but quite safe
    # coords = []
    # ol = LineString(line(cartesian(thetas[0], rhos[0]), angles[0], length))
    # lin = []
    # for i in range(0, len(thetas)):
    #    lin.append(Line(cartesian(thetas[i], rhos[i]), slope=np.tan(angles[i])))

    # print(coords)
    # ax = plt.subplot(111)
    # ax.plot(*zip(*coords))
    # plt.show()

    # return polar(*coords)
        # l = LineString(line(cartesian(thetas[i], rhos[i]), angles[i], length))
        # coords.append(l.intersection(ol))  # Wrong
        # ol = l
        # coords.append(line(cartesian(thetas[i], rhos[i]), angles[i], length))
    #multiline = MultiLineString(coords)

    #r = []
    #linestring = LineString(((0, 0), (0, 0)))
    #for theta in thetas:
     #   rho = 0
     #   linestring.coords[1] = cartesian(theta, rho)
     #   while not linestring.intersects(multiline):
     #       rho += 1
     #   r.append(rho)

    #x, y = multiline.xy
    #ax = plt.subplot(111, polar=True)
    #ax.plot(thetas, r)
    #plt.show()
    #ev = multiline.envelope
    #return polar(multiline.envelope.interiors[0].coords)


# Works but super slow
def lines_sympy(theta, rho, angle):
    rays = []
    for t in theta:
        rays.append(Ray(Point(0, 0), angle=t))

    coords = np.empty([2, len(theta)])
    for i in range(0, len(theta)):
        l = Line((cartesian(theta[i], rho[i])), slope=np.tan(angle[i]))
        first_inter, dist = None, None

        for ray in rays:
            t = time()
            inter = l.intersection(ray)
            print(1, time() - t)
            if len(inter):
                inter_dist = (inter[0].x.evalf()**2+inter[0].y.evalf()**2)**(1/2)
                if first_inter is None or inter_dist < dist:
                    first_inter = inter[0]
                    dist = inter_dist

        # What if first_inter == None ? shouldn't happend
        coords[:, i] = first_inter.x, first_inter.y
    return polar(*coords)


def first_intersection(angle, xs, ys, slopes):
    for i in 1:
        x = 0


def circles(thetas, rhos, radius, ccw):
    # Clipper works only with integers, scaling needed
    p = cartesian(thetas, rhos)
    # minp = np.min(np.absolute(p[np.nonzero(p)]))
    maxp = np.max(np.absolute(p))
    scale = len(thetas) / maxp  # reasonable
    p *= scale
    coords = p.astype(int)
    pco = pyclipper.PyclipperOffset()
    pco.AddPath(coords, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    result = pco.Execute(-radius*scale)[0]
    p = polar(*zip(*result))
    p[1] /= scale
    return p

    # fast but spikes on discontinuities
    # rho = np.empty(len(thetas))
    # # TODO Fix ccw
    # for i in range(-1, len(thetas)):
    #     dtheta = thetas[i]-thetas[i-1]
    #     if i != -1 and rhos[i-1]**2 + rhos[i]**2 - 2*rhos[i-1]*rhos[i]*np.cos(dtheta) <= 0:  # usually only when i=0
    #         rho[i] = rho[i-1]
    #         continue
    #     cos_a = rhos[i-1] * np.sin(dtheta) / np.sqrt((rhos[i-1]**2 + rhos[i]**2 - 2*rhos[i-1]*rhos[i]*np.cos(dtheta)))
    #     rho[i] = rhos[i] - radius / cos_a
    #     if i==209:
    #         None
    # return thetas, rho

    # superslow and buggy
    # coords = cartesian(thetas, rhos)
    # coords = list(zip(coords[0], coords[1]))
    # coords.extend(coords[0:2])
    # ring = LinearRing(coords)
    # x, y = ring.parallel_offset(radius, 'right' if ccw else 'left', resolution=len(thetas)*2).xy
    # return polar(x, y)


# def line(p, angle, length):
#     x, y = p
#     return (x-length/2*np.cos(angle), y-length/2*np.sin(angle)), (x+length/2*np.cos(angle), y+length/2*np.sin(angle))
