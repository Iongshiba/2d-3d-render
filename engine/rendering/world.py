from __future__ import annotations

import numpy as np
from utils.transform import *


class Transform:
    def __init__(self, animate=None):
        self.matrix = np.identity(4)
        self.animate = animate

    def get_matrix(self):
        return self.matrix

    def update_matrix(self, dt):
        if self.animate:
            self.animate(self, dt)


class Translate(Transform):
    def __init__(self, x=0.0, y=0.0, z=0.0, animate=None):
        super().__init__(animate)
        self.x = x
        self.y = y
        self.z = z

    def get_matrix(self):
        return translate(self.x, self.y, self.z)


class Scale(Transform):
    def __init__(self, x, y=None, z=None, animate=None):
        super().__init__(animate)
        self.x = x
        self.y = y
        self.z = z

    def get_matrix(self):
        return scale(self.x, self.y, self.z)


class Rotate(Transform):
    def __init__(self, axis=(1.0, 0.0, 0.0), angle=0.0, radians=None, animate=None):
        super().__init__(animate)
        self.axis = axis
        self.angle = angle
        self.radians = radians

    def get_matrix(self):
        return rotate(self.axis, self.angle, self.radians)


__all__ = ["Transform", "Translate", "Scale", "Rotate"]
