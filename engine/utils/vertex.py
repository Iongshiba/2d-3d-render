import numpy as np


def vertices_to_coords(vertices):
    return np.array([o.vertex.flatten() for o in vertices], dtype=np.float32)


def vertices_to_colors(vertices):
    return np.array([o.color.flatten() for o in vertices], dtype=np.float32)
