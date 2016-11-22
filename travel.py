import fileio
import interpolation
import numpy as np


class Travel:
    x, y, xpoints, ypoints, levels, l, interp, order, steps, n =\
        None, None, None, None, None, None, None, None, None, None

    def __call__(self):
        return self.x is not None

    def load(self, filename):
        try:
            self.x, self.y = fileio.read(filename)
            self.xpoints, self.ypoints, self.levels, self.l = None, None, None, None
        except FileNotFoundError:
            print('File not found')
        except ValueError:
            print('Malformed input file')

    def gen(self, filename, interp, order, steps, n):
        try:
            self.xpoints, self.ypoints, self.levels = fileio.read(filename)
        except FileNotFoundError:
            print('File not found')
        except ValueError:
            print('Malformed input file')

        self.l = not not self.levels  # True if levels are used

        self.update(interp, order, steps, n)


    def update(self, interp=None, order=None, steps=None, n=None):
        if interp is not None:
            self.interp = interp
        if order is not None:
            self.order = order
        if steps is not None:
            self.steps = steps
        if n is not None:
            self.n = n

        # Warns if levels aren't respected
        if self.l and self.interp in ['spline']:
            print('Warning: levels not respected in', self.interp, 'interpolation')

        x, y = [], []

        if self.interp == 'spline':
            x, y = interpolation.spline(self.xpoints, self.ypoints, self.order, self.steps)
        elif self.interp == 'linear':
            x, y = interpolation.linear(self.xpoints, self.ypoints, self.steps)
            # x, y = self.xpoints, self.ypoints  # more sense
        elif self.interp in ['harmonic', 'cycloidal', 'parabolic']:
            if self.l:
                x, y = interpolation.lev(self.interp, self.levels, self.steps)
            else:
                x, y = interpolation.points(self.interp, self.xpoints, self.ypoints, self.steps)
        elif self.interp == 'polynomial':
            if self.l:
                x, y = interpolation.lev(self.interp, self.levels, self.steps, self.order)
            else:
                x, y = interpolation.points(self.interp, self.xpoints, self.ypoints, self.steps, self.order)

        # Fixing x to [0;1]
        pts = [i for i, p in enumerate(x) if p >= 1]
        if len(pts):
            first = pts[0]  # find index of first point with x >= 1
            x = [p-1 for p in x[first:]] + x[:first-1]
            y = y[first:] + y[:first-1]

        # Tile the profile
        self.x = []
        for i in range(0, self.n):
            self.x.extend([p+i for p in x])  # increment x elements by i, performance is critic
        self.y = np.tile(y, self.n)
