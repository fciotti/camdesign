import fileio
import interpolation
import numpy as np
from sympy import sympify
from sympy.utilities.lambdify import lambdify
from utils import HandledValueError
from sympy.abc import x


class Travel:
    x, y, xpoints, ypoints, levels, l, f, x0, x1, interp, order, steps, n =\
        None, None, None, None, None, None, None, None, None, None, None, None, None

    def __call__(self):
        return self.x is not None

    def __getattr__(self, name):
        if name == 'l':
            return not not self.levels  # True if levels are used

    def load(self, filename):
        self.x, self.y = fileio.read(filename)
        self.xpoints, self.ypoints, self.levels, self.f = None, None, None, None

    def gen(self, filename, f, x0, x1, interp, order, steps, n):
        if filename is None:
            self.xpoints, self.ypoints, self.levels, self.f = None, None, None, None
            try:
                if f[0] == f[-1] == '"' or f[0] == f[-1] == "'":
                    f = f[1:-1]
                self.f = lambdify(x, sympify(f), modules="numpy")
                print(self.f(np.array([0, 1])))
            except:
                raise HandledValueError('Malformed expression')
        else:
            self.f = None
            self.xpoints, self.ypoints, self.levels = fileio.read(filename)
        self.update(x0, x1, interp, order, steps, n)

    def update(self, x0=None, x1=None, interp=None, order=None, steps=None, n=None):
        if x0 is not None:
            self.x0 = x0
        if x1 is not None:
            self.x1 = x1
        if interp is not None:
            self.interp = interp
        if order is not None:
            self.order = order
        if steps is not None:
            self.steps = steps
        if n is not None:
            self.n = n

        if self.xpoints is None:
            x = np.linspace(self.x0, self.x1, num=self.steps)
            try:
                y = self.f(x)
            except:
                raise HandledValueError('Malformed expression')
            self.x = np.linspace(0, 1, num=self.steps*self.n)
        else:
            # Warning if levels aren't respected
            if self.l and self.interp in ['spline']:
                print('Warning: levels not respected in', self.interp, 'interpolation')

            x, y = [], []

            if self.interp == 'spline':
                x, y = interpolation.spline(self.xpoints, self.ypoints, self.order, self.steps)
            elif self.interp == 'linear':
                x, y = interpolation.linear(self.xpoints, self.ypoints, self.steps)
                # x, y = self.xpoints, self.ypoints  # more sense, some problems with cam
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

            # Fix x to [0;1]
            pts = [i for i, p in enumerate(x) if p >= 1]
            if len(pts) and self.interp not in ['linear', 'spline']:
                first = pts[0]  # find index of first point with x > 1
                x = [p-1 for p in x[first:]] + x[:first+1]
                y = y[first:] + y[:first+1]

            # Tile the profile
            self.x = np.empty([len(x)*self.n])
            for i in range(0, self.n):
                self.x.put(np.arange(i*len(x), (i+1)*len(x)), [(p+i)/self.n for p in x])  # increment x elements by i
        self.y = np.tile(y, self.n)
