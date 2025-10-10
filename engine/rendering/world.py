from __future__ import annotations

import numpy as np
from utils.transform import *


class Transform:
    def __init__(self):
        self.matrix = np.identity(4)

    def get_matrix(self):
        return self.matrix

    # def combine(self, matrices):
    #     mats = vec(matrices)
    #     if mats.size == 0:
    #         return identity()

    #     if len(mats) == 1:
    #         result = mats[0]
    #     else:
    #         result = reduce(np.dot, mats)

    #     return result

    # def get_identity_matrix(self):
    #     return identity()

    # def get_scale_matrix(self, x, y=None, z=None):
    #     return scale(x, y, z)

    # def get_translate_matrix(self, x=0.0, y=0.0, z=0.0):
    #     return translate(x, y, z)

    # def get_rotate_matrix(axis=(1.0, 0.0, 0.0), angle=0.0, radians=None):
    #     return rotate(axis, angle, radians)


class Translate(Transform):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.matrix = translate(x, y, z)


class Scale(Transform):
    def __init__(self, x, y=None, z=None):
        self.matrix = scale(x, y, z)


class Rotate(Transform):
    def __init__(self, axis=(1.0, 0.0, 0.0), angle=0.0, radians=None):
        self.matrix = scale(axis, angle, radians)


__all__ = ["Transform", "Translate", "Scale", "Rotate"]
