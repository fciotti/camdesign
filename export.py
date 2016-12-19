import numpy as np
from stl import mesh
from scipy.spatial import Delaunay
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
from utils import cartesian


def stl(cam, filename, width, conj=False):
    if conj:
        points = cartesian(*cam.conj_pcoords)
    else:
        points = cam.points
    
    # 2D Delaunay triangulation for front face and building of lower and upper faces
    tri0 = points[Delaunay(points).simplices]
    tri1 = np.concatenate((tri0, np.zeros([tri0.shape[0], tri0.shape[1], 1])), 2)
    tri2 = np.concatenate((tri0, np.ones([tri0.shape[0], tri0.shape[1], 1]) * width), 2)

    # Build triangles for side face
    vertices1 = np.concatenate((points, np.zeros([points.shape[0], 1])), 1)
    vertices2 = np.concatenate((points, np.ones([points.shape[0], 1]) * width), 1)
    tri3_1 = np.empty([points.shape[0], 3, 3])
    tri3_2 = np.empty_like(tri3_1)
    for i in range(0, vertices1.shape[0]):
        tri3_1[i] = [vertices1[i-1], vertices1[i], vertices2[i]]
        tri3_2[i] = [vertices2[i-1], vertices2[i], vertices1[i-1]]

    # Concatenate and save
    tri = np.concatenate((tri1, tri2, tri3_1, tri3_2))
    data = np.zeros(tri.shape[0], dtype=mesh.Mesh.dtype)
    data['vectors'] = tri
    prism = mesh.Mesh(data)
    prism.save(filename)

    # Ugly plotting
    fig = plt.figure()
    ax = mplot3d.Axes3D(fig)
    ax.add_collection3d(mplot3d.art3d.Poly3DCollection(prism.vectors))

    # Auto scale
    scale = prism.points.flatten(-1)
    ax.auto_scale_xyz(scale, scale, scale)

    plt.show()
