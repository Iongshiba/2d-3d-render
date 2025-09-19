import numpy as np


class Vertex:
    def __init__(self, x, y, z):
        self.vertex = np.array([x, y, z], dtype=np.float32)
        self.color = np.random.rand(3).astype(np.float32)
