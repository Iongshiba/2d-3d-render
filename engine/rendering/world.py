from __future__ import annotations

from functools import reduce
from typing import Iterable, Sequence

import numpy as np


class Transform:
    def __init__(self):
        self.identity = np.identity(4, dtype=np.float32)
        self.alpha: float = 1.0
        self.delta: float = 0.005

    def combine(self, matrices):
        mats = [np.array(m, dtype=np.float32) for m in matrices]
        if not mats:
            return self.identity.copy()

        if self.alpha <= -5 or self.alpha >= 5:
            self.delta *= -1
        self.alpha += self.delta

        if len(mats) == 1:
            result = mats[0]
        else:
            result = reduce(np.dot, mats)

        return result

    def get_scale_matrix(self, factor):
        matrix = self.identity.copy()
        matrix[0, 0] = matrix[1, 1] = matrix[2, 2] = np.float32(factor)
        return matrix

    def get_translate_matrix(self, x=0.0, y=0.0, z=None):
        matrix = self.identity.copy()
        matrix[0, 3] = np.float32(x)
        matrix[1, 3] = np.float32(y)
        matrix[2, 3] = np.float32(z)
        return matrix

    def get_rotate_matrix(self, axis="x", angle=None):
        angle = float(self.alpha if angle is None else angle)
        c = np.float32(np.cos(angle))
        s = np.float32(np.sin(angle))
        matrix = self.identity.copy()

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

    def project(
        self,
        fov=90.0,
        aspect_ratio=1.0,
        near=0.1,
        far=100.0,
    ):
        fov_rad = np.radians(fov)
        f = np.float32(1.0 / np.tan(fov_rad / 2.0))
        near = np.float32(near)
        far = np.float32(far)

        matrix = self.identity.copy()
        matrix[0, 0] = f / np.float32(aspect_ratio)
        matrix[1, 1] = f
        matrix[2, 2] = (far + near) / (near - far)
        matrix[2, 3] = (2.0 * far * near) / (near - far)
        matrix[3, 2] = -1.0
        matrix[3, 3] = 0.0
        return matrix

    def look_at(
        self,
        camera_pos,
        target_pos,
        world_up=(0.0, 1.0, 0.0),
    ):
        camera_pos = np.array(camera_pos, dtype=np.float32)
        target_pos = np.array(target_pos, dtype=np.float32)
        world_up = np.array(world_up, dtype=np.float32)

        direction = target_pos - camera_pos
        right = np.cross(direction, world_up)
        up = np.cross(direction, right)

        direction = self._normalize(direction)
        right = self._normalize(right)
        up = self._normalize(up)

        rotate = self.identity.copy()
        rotate[0:3, 0] = right
        rotate[0:3, 1] = up
        rotate[0:3, 2] = direction

        translate = self.identity.copy()
        translate[0:3, 3] = -camera_pos

        return np.dot(rotate, translate)

    @staticmethod
    def _normalize(vector):
        norm = float(np.linalg.norm(vector))
        if norm < 1e-6:
            return np.zeros_like(vector)
        return vector / norm


__all__ = ["Transform"]
