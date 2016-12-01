import numpy as np
from stl import mesh
from scipy.spatial import Delaunay
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


def stl(cam, filename):

    # vertices = np.concatenate((vertices, np.concatenate((cam.points, np.ones([cam.points.shape[0], 1])*5), 1)))
    # f = 2 + vertices[0].length
    # print(vertices1)
    # tri1 = vertices1[Delaunay(vertices1).simplices]
    # tri2 = vertices2[Delaunay(vertices2).simplices]
    tri0 = cam.points[Delaunay(cam.points).simplices]
    tri1 = np.concatenate((tri0, np.zeros([tri0.shape[0], tri0.shape[1], 1])), 2)
    tri2 = np.concatenate((tri0, np.ones([tri0.shape[0], tri0.shape[1], 1])*5), 2)
    vertices1 = np.concatenate((cam.points, np.zeros([cam.points.shape[0], 1])), 1)
    vertices2 = np.concatenate((cam.points, np.ones([cam.points.shape[0], 1]) * 5), 1)
    tri3_1 = np.empty([cam.points.shape[0], 3, 3])
    tri3_2 = np.empty_like(tri3_1)
    for i in range(0, vertices1.shape[0]):
        tri3_1[i] = [vertices1[i-1], vertices1[i], vertices2[i]]
        tri3_2[i] = [vertices2[i-1], vertices2[i], vertices1[i-1]]
    tri = np.concatenate((tri1, tri2, tri3_1, tri3_2))
    data = np.zeros(tri.shape[0], dtype=mesh.Mesh.dtype)
    data['vectors'] = tri
    prism = mesh.Mesh(data)
    prism.save(filename)

    fig = plt.figure()
    ax = mplot3d.Axes3D(fig)
    ax.add_collection3d(mplot3d.art3d.Poly3DCollection(prism.vectors))

    # Auto scale
    scale = prism.points.flatten(-1)
    ax.auto_scale_xyz(scale, scale, scale)

    plt.show()
