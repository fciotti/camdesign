import numpy as np
import fileio


class Cam:
    theta, rho, loaded, radius, ccw = None, None, None, None, None

    def __call__(self):
        return self.theta is not None

    def __init__(self, travel, follower):
        self.travel = travel
        self.follower = follower

    def gen(self, radius=None, ccw=None):
        if radius is not None:
            self.radius = radius
        if ccw is not None:
            self.ccw = ccw
        self.loaded = False
        self.theta = np.linspace(0, 2 * np.pi, len(self.travel.y))
        if self.ccw:
            self.theta = self.theta[::-1]
        if self.follower.kind == 'knife':
            if self.follower.offset == 0:
                self.rho = self.travel.y + self.radius
            else:
                if self.follower.offset > self.radius:
                    print('Offset must be smaller than radius')
                    return
                h0 = np.math.sqrt(self.radius**2-self.follower.offset**2)
                self.rho = np.sqrt((self.travel.y+h0)**2+self.follower.offset**2)
                # self.rho = self.radius / (1 - self.travel.y / self.follower.offset) wrong
        elif self.follower == 'roller':
            if self.follower.offset == 0:
                self.rho = self.travel.y + self.radius
            else:
                return
        elif self.follower == 'flat':
            return

    def load(self, filename):
        try:
            self.theta, self.rho = fileio.read(filename)
            self.loaded = True
        except FileNotFoundError:
            print('File not found')
        except ValueError:
            print('Malformed input file')
