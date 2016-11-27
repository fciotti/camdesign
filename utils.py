import numpy as np
import sys


class HandledValueError(ValueError):
    pass


def cartesian(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return np.array([x, y]).T


def polar(x, y):
    theta = np.arctan2(y, x)
    rho = np.sqrt(np.square(x) + np.square(y))
    return np.array([theta, rho])


def plot_polar(*args):
    result = []
    for i in range(0, len(args), 2):
        result.extend(cartesian(args[i], args[i+1]).T)
    return result


class Progress:
    def __init__(self):
        print('Progress: 0 %', end='')
        sys.stdout.flush()
        self.progress = 0

    def __call__(self, progress):
        prog = int(progress*100)
        if prog != self.progress:
            print('\rProgress:', prog, '%', end='')
            sys.stdout.flush()
        self.progress = prog

    def close(self):
        print('\rProgress: 100 %')
