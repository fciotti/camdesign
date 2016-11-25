import numpy as np
import fileio
import envelope


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
        self.theta = np.multiply(self.travel.x, 2 * np.pi)
        if self.ccw:
            self.theta = self.theta[::-1]
        if self.follower.kind == 'knife':
            if self.follower.offset == 0:
                self.rho = self.travel.y + self.radius
            else:
                self.rho = np.sqrt(self.follower.offset**2+(self.radius+self.travel.y)**2)
        elif self.follower.kind == 'roller':
            if self.follower.offset == 0:
                self.rho = self.travel.y + self.radius - self.follower.radius
            else:
                rho_center = np.sqrt(self.follower.offset ** 2 + (self.radius + self.travel.y) ** 2)
                self.theta, self.rho = envelope.circles(self.theta, rho_center, self.follower.radius, self.ccw)
        elif self.follower.kind == 'flat':
            self.theta, self.rho = envelope.lines(self.theta, self.travel.y + self.radius, self.theta+np.pi/2)
            None

    def load(self, filename):
        try:
            self.theta, self.rho = fileio.read(filename)
            self.loaded = True
        except FileNotFoundError:
            print('File not found')
        except ValueError:
            print('Malformed input file')
