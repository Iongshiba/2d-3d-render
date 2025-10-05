from __future__ import annotations

from functools import reduce
from typing import Iterable, Sequence

import numpy as np
from utils.transform import *


class Transform:
    def __init__(self):
        self.alpha: float = 1.0
        self.speed: float = 0.5

    def process_time(self, step_scale=1.0):
        if self.alpha <= -10 or self.alpha >= 10:
            self.speed *= -1
        self.alpha += self.speed * step_scale

    def combine(self, matrices):
        mats = vec(matrices)
        if mats.size == 0:
            return identity()

        if len(mats) == 1:
            result = mats[0]
        else:
            result = reduce(np.dot, mats)

        return result

    def get_identity_matrix(self):
        return identity()

    def get_scale_matrix(self, x, y=None, z=None):
        return scale(x, y, z)

    def get_translate_matrix(self, x=0.0, y=0.0, z=0.0):
        return translate(x, y, z)

    def get_rotate_matrix(axis=(1.0, 0.0, 0.0), angle=0.0, radians=None):
        return rotate(axis, angle, radians)

    @staticmethod
    def _normalize(vector):
        norm = float(np.linalg.norm(vector))
        if norm < 1e-6:
            return np.zeros_like(vector)
        return vector / norm


__all__ = ["Transform"]
