import numpy as np


class Vertex:
    def __init__(self, x, y, z):
        self.vertex = np.array([x, y, z], dtype=np.float32)
        self.color = np.float32(np.random.rand(1, 3))
