import numpy as np
import fileio
import envelope
from utils import *
from time import time


class Cam:
    pcoords, loaded, radius, ccw, conj_pcoords, breadth = None, None, None, None, None, None

    def __call__(self):
        return self.pcoords is not None

    def conj(self):
        return self.conj_pcoords is not None

    def __init__(self, travel, follower):
        self.travel = travel
        self.follower = follower

    def gen(self, radius=None, ccw=None):
        if radius is not None:
            self.radius = radius
        if ccw is not None:
            self.ccw = ccw
        self.loaded = False
        self.conj_pcoords = None
        self.pcoords = np.empty([2, len(self.travel.x)])
        self.pcoords[0] = np.multiply(self.travel.x, 2 * np.pi)
        if self.ccw:
            self.pcoords[0] = self.pcoords[0][::-1]
        if self.follower.kind == 'knife':
            if self.follower.offset == 0:
                self.pcoords[1] = self.travel.y + self.radius
            else:
                self.pcoords[1] = np.sqrt(self.follower.offset**2+(self.radius+self.travel.y)**2)
        elif self.follower.kind == 'roller':
            if self.follower.offset == 0:
                self.pcoords[1] = self.travel.y + self.radius - self.follower.radius
            else:
                rho_trace = np.sqrt(self.follower.offset ** 2 + (self.radius + self.travel.y) ** 2)
                self.pcoords = envelope.circles(self.pcoords[0], rho_trace, self.follower.radius, self.ccw)
        elif self.follower.kind == 'flat':
            self.pcoords = envelope.lines(self.pcoords[0], self.travel.y + self.radius, self.pcoords[0]+np.pi/2)

    def load(self, filename):
        self.pcoords = fileio.read(filename)
        self.loaded = True
        self.conj_pcoords = None

    def gen_conjugated(self, breadth=None):
        # Only flat follower and others with diametrically opposed followers
        if breadth is None:
            breadth = self.breadth
        if breadth == 0:
            # Set breadth = max cam diameter
            print('Searching optimal breadth')
            progress = Progress()
            for i, p in enumerate(self.pcoords.T):
                b = p[1] + self.pcoords[1][np.absolute(np.unwrap(self.pcoords[0]-p[0]-np.pi)).argmin()]
                if b > breadth:
                    breadth = b
                progress(i/len(self.pcoords.T))
            progress.close()
        elif breadth < np.max(self.pcoords[1]):
            # maybe could be, with opposed values must sum > 0
            raise HandledValueError('Breadth must be >= max radius ({:.3g})'.format(np.max(self.pcoords[1])))
        self.breadth = breadth
        print('Breadth:', breadth)
        self.conj_pcoords = np.empty_like(self.pcoords)
        for i in range(0, len(self.pcoords.T)):
            self.conj_pcoords[:, i] = (self.pcoords[0, i]+np.pi) % (2*np.pi), breadth - self.pcoords[1][i]
        # just fast, but probably would be enough a shift
        self.conj_pcoords = self.conj_pcoords[:, self.conj_pcoords[0].argsort()]
