import numpy as np
import fileio
import envelope
from utils import cartesian, HandledValueError, Progress
from scipy.interpolate import interp1d


class Cam:
    pcoords, _points, f, rho_trace, spline, loaded, radius, ccw, conj_pcoords, breadth, width =\
        None, None, None, None, None, None, None, None, None, None, None

    def __getattr__(self, name):
        if name == 'theta':
            return self.pcoords[0]
        elif name == 'rho':
            return self.pcoords[1]
        elif name == 'ppoints':
            return self.pcoords.T
        elif name == 'points':
            if self._points is None:
                self._points = cartesian(*self.pcoords)
            return self._points
        elif name == 'coords':
            return self.points.T
        return None

    # Return cartesian coords after a theta0 counterclockwise rotation
    def rot_coords(self, theta0):
        return cartesian(self.theta + theta0, self.rho).T

    # Return rho at given theta
    def interp(self, theta):
        return self.f(theta % 2*np.pi)

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
        self._points = None
        self.conj_pcoords = None
        self.pcoords = np.empty([2, len(self.travel.x)])
        self.pcoords[0] = np.multiply(self.travel.x, 2 * np.pi)

        if self.follower.kind == 'knife':
            if self.follower.offset == 0:
                self.pcoords[1] = self.travel.y + self.radius
            else:
                self.pcoords[1] = np.sqrt(self.follower.offset**2+(self.radius+self.travel.y)**2)
        elif self.follower.kind == 'roller':
            if self.follower.offset == 0:
                self.pcoords[1] = self.travel.y + self.radius - self.follower.radius
            else:
                self.rho_trace = np.sqrt(self.follower.offset ** 2 + (self.radius + self.travel.y) ** 2)
                self.pcoords = envelope.roller(self.pcoords[0], self.rho_trace, self.follower.radius)
        elif self.follower.kind == 'flat':
            self.pcoords = envelope.flat(np.array([self.pcoords[0], self.travel.y + self.radius]))
            # self.pcoords = envelope.flat2(self.pcoords[0], self.travel.y + self.radius, self.pcoords[0]+np.pi/2)
        if self.ccw:
            self.pcoords[1] = self.pcoords[1][::-1]

        # Fixing x to [0;2pi], needed only for a few things
        self.pcoords[0] %= 2*np.pi
        if self.pcoords[0][-1] == 0:
            self.pcoords[0][-1] = 2*np.pi
        self.pcoords = self.pcoords[:, self.pcoords[0].argsort()]

        # pts = [i for i, p in enumerate(self.pcoords[0]) if p >= 0]
        # if len(pts):
        #     first = pts[0]  # find index of first point with theta >= 0
        #     self.pcoords[0] = self.pcoords[0][first:] + self.pcoords[0][:first + 1]
        #     self.pcoords[1] = self.pcoords[1][first:] + self.pcoords[1][:first + 1]

        self.f = interp1d(*self.pcoords)
        # self.spline = splrep(*self.pcoords, per=True)

    def load(self, filename):
        self.pcoords = fileio.read(filename)
        self._points = None
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
                b = p[1] + self.interp(p[0]+np.pi)  # self.near_rho(p[0]+np.pi)
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
