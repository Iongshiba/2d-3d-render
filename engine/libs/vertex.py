import numpy as np


class Vertex:
    def __init__(self, x, y, z):
        self.vertex = np.array([x, y, z], dtype=np.float32)
        r = np.random.uniform(0.9, 1.0)  # small red
        g = np.random.uniform(0.5, 0.6)  # small green
        b = np.random.uniform(0.0, 1.0)  # strong blue

        self.color = np.array([r, g, b], dtype=np.float32)
