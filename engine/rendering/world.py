from __future__ import annotations

from functools import reduce
from typing import Iterable, Sequence

import numpy as np


class Transform:
    def __init__(self):
        self.identity = np.identity(4, dtype=np.float32)
        self.alpha: float = 1.0
        self.speed: float = 0.5

    def process_time(self, step_scale=1.0):
        if self.alpha <= -10 or self.alpha >= 10:
            self.speed *= -1
        self.alpha += self.speed * step_scale

    def combine(self, matrices):
        mats = [np.array(m, dtype=np.float32) for m in matrices]
        if not mats:
            return self.identity.copy()

        if len(mats) == 1:
            result = mats[0]
        else:
            result = reduce(np.dot, mats)

        return result

    def get_identity_matrix(self):
        return self.identity.copy()

    def get_scale_matrix(self, factor):
        matrix = self.identity.copy()
        scale_value = np.float32(self.alpha if factor is None else factor)
        matrix[0, 0] = matrix[1, 1] = matrix[2, 2] = scale_value
        return matrix

    def get_translate_matrix(self, x=0.0, y=0.0, z=0.0):
        matrix = self.identity.copy()
        x_value = np.float32(self.alpha if x is None else x)
        y_value = np.float32(self.alpha if y is None else y)
        z_value = np.float32(self.alpha if z is None else z)
        matrix[0, 3] = x_value
        matrix[1, 3] = y_value
        matrix[2, 3] = z_value
        return matrix

    def get_rotate_matrix(self, axis="x", angle=None):
        matrix = self.identity.copy()
        angle = np.float32(self.alpha if angle is None else angle)
        c = np.float32(np.cos(angle))
        s = np.float32(np.sin(angle))

        axis = axis.lower()
        if axis == "x":
            matrix[1, 1] = c
            matrix[1, 2] = -s
            matrix[2, 1] = s
            matrix[2, 2] = c
        elif axis == "y":
            matrix[0, 0] = c
            matrix[0, 2] = s
            matrix[2, 0] = -s
            matrix[2, 2] = c
        elif axis == "z":
            matrix[0, 0] = c
            matrix[0, 1] = -s
            matrix[1, 0] = s
            matrix[1, 1] = c
        return matrix

    @staticmethod
    def _normalize(vector):
        norm = float(np.linalg.norm(vector))
        if norm < 1e-6:
            return np.zeros_like(vector)
        return vector / norm


__all__ = ["Transform"]
