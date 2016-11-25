import numpy as np
from shapely.geometry import MultiLineString, LineString, LinearRing
import matplotlib.pyplot as plt
from sympy import N
from sympy.geometry import *


def lines(thetas, rhos, angles):
    length = max(rhos)*100  # Dirty but quite safe
    coords = []
    # ol = LineString(line(cartesian(thetas[0], rhos[0]), angles[0], length))
    lin = []
    for i in range(0, len(thetas)):
        lin.append(Line(cartesian(thetas[i], rhos[i]), slope=np.tan(angles[i])))

    for theta in thetas:
        Ray(Point(0, 0), angle=theta)
        coords.append((float(rv.x.evalf()), float(rv.y.evalf())))

    print(coords)
    ax = plt.subplot(111)
    ax.plot(*zip(*coords))
    plt.show()

    return polar(coords)
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


def first_intersection(angle, xs, ys, slopes):
    for i in len(xs):
        x = 0


# Super slow
def first_intersection_slow(obj, collection):
    first = None
    for l in collection:
        intersections = obj.intersection(l)
        if len(intersections):
            r = intersections[0]
        if first is None or r.distance(Point(0, 0)) < first.distance(Point(0, 0)):
            first = r
    return first


def circles(thetas, rhos, radius, ccw):
    coords = cartesian(thetas, rhos)
    coords = list(zip(coords[0], coords[1]))
    coords.extend(coords[0:2])
    ring = LinearRing(coords)
    x, y = ring.parallel_offset(radius, 'right' if ccw else 'left', resolution=len(thetas)*2).xy
    return polar(x, y)


def line(p, angle, length):
    x, y = p
    return (x-length/2*np.cos(angle), y-length/2*np.sin(angle)), (x+length/2*np.cos(angle), y+length/2*np.sin(angle))


def cartesian(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y


def polar(x, y):
    theta = np.arctan2(y, x)
    rho = np.sqrt(np.square(x) + np.square(y))
    return theta, rho
