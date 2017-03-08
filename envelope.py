import pyclipper
import numpy as np
from utils import cartesian, polar


# Super fast
def flat(pcoords):
    result = np.empty_like(pcoords)
    result[0] = pcoords[0]
    for i, theta0 in enumerate(pcoords[0]):
        distances = pcoords[1] / np.cos(pcoords[0] - theta0)
        result[1][i] = np.min(distances[distances > 0])
    return result


# Fast
def roller(thetas, rhos, radius):
    # Clipper works only with integers, scaling needed
    p = cartesian(thetas, rhos)
    scale = 1/(rhos.max()*(1-np.cos(np.pi/thetas.shape[0])))  # very good
    p *= scale
    coords = p.astype(int)
    pco = pyclipper.PyclipperOffset()
    pco.AddPath(coords, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    result = pco.Execute(-radius*scale)[0]
    p = polar(*zip(*result))
    p[1] /= scale
    return p
