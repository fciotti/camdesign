import numpy as np
from scipy import interpolate
from utils import HandledValueError


def spline(xpoints, ypoints, steps, order):
    if order > 5 or order >= len(xpoints):
        raise HandledValueError('Spline order must be smaller than number of points and not greater than 5')
    tck = interpolate.splrep(xpoints, ypoints, k=order, per=True)
    x = np.linspace(0, 1, steps)
    y = interpolate.splev(x, tck)
    return x, y


def linear(xpoints, ypoints, steps):
    f = interpolate.interp1d([xpoints[-2]-1, xpoints[-1]-1] + xpoints, [ypoints[-2], ypoints[-1]] + ypoints)
    x = np.linspace(0, 1, steps)
    y = f(x)
    return x, y


def points(kind, xpoints, ypoints, steps, order=None):
    x, y = [], []
    for i in range(0, len(xpoints) - 1):
        x0 = xpoints[i]
        y0 = ypoints[i]
        if kind == 'polynomial':
            xs, ys = func(kind, x0, xpoints[i + 1], y0, ypoints[i + 1], steps, order)
        else:
            xs, ys = func(kind, x0, xpoints[i + 1], y0, ypoints[i + 1], steps)
        x.extend(xs)
        y.extend(ys)
    return x, y


def func(kind, *args, **kwargs):
    if kind == 'harmonic':
        return harmonic(*args, **kwargs)
    elif kind == 'cycloidal':
        return cycloidal(*args, **kwargs)
    elif kind == 'parabolic':
        return parabolic(*args, **kwargs)
    elif kind == 'polynomial':
        return polynomial(*args, **kwargs)
    else:
        raise HandledValueError


def harmonic(x0, x1, y0, y1, steps):
    x = np.linspace(x0, x1, steps)
    y = y0 + (y1-y0)/2*(1-np.cos(np.divide(np.pi*(x+(-x0)), x1-x0)))
    return x, y


def cycloidal(x0, x1, y0, y1, steps):
    x = np.linspace(x0, x1, steps)
    r = np.divide(x+(-x0), x1-x0)
    y = y0 + (y1-y0)/np.pi*(np.pi*r-np.sin(2*np.pi*r)/2)
    return x, y


def parabolic(x0, x1, y0, y1, steps):
    x = np.linspace(x0, (x0+x1)/2, steps)
    r = np.divide(x + (-x0), x1 - x0)
    y = y0 + 2*(y1-y0)*r**2
    x2 = np.linspace((x0+x1)/2, x1, steps)
    r2 = np.divide(x2 + (-x0), x1 - x0)
    y2 = y0 + (y1-y0)*(1-2*(1-r2)**2)
    return np.concatenate((x, x2)), np.concatenate((y, y2))


def polynomial(x0, x1, y0, y1, steps, order):
    # Vandermonde matrix
    A = np.zeros((2+order*2, 2+order*2))

    B = np.zeros(2+order*2)

    B[0] = 0
    B[1] = y1-y0

    for col in range(0, 2+order*2):
        A[0, col] = 0 ** col
        A[1, col] = (x1-x0) ** col

    for deriv in range(1, order + 1):
        B[deriv*2] = 0
        B[1+deriv*2] = 0
        for col in range(0, 2+order*2):
            A[deriv*2, col] = der(0, col, deriv)
            A[1+deriv*2, col] = der((x1-x0), col, deriv)

    c = np.linalg.solve(A, B)

    x = np.linspace(0, x1-x0, steps)
    y = np.polyval(c[::-1], x)

    return x+x0, y+y0


# k-th derivative of x^n
def der(x, n, k):
    if k > n:
        return 0
    return np.math.factorial(n)/np.math.factorial(n-k)*x**(n-k)
