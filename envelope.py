import pyclipper
import numpy as np
from utils import cartesian, polar


# Super fast
def flat(pcoords):
    res = np.copy(pcoords)
    tmp = np.empty_like(pcoords[0])
    for i, theta0 in enumerate(pcoords[0]):
        rr = pcoords[1] / np.cos(pcoords[0] - theta0)
        res[1][i] = np.min(rr[rr > 0])
    return res


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
    print(len(p[0]))
    return p
