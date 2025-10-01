from __future__ import annotations

from dataclasses import replace

import numpy as np

from config import CameraConfig
from core.enums import CameraMovement


class Camera:
    def __init__(self, config=None):
        self.config = CameraConfig() if config is None else replace(config)
        self.aspect_ratio: float = 1.0

        # Internal state vectors
        self.position: np.ndarray
        self.front: np.ndarray
        self.world_up: np.ndarray
        self.right: np.ndarray
        self.up: np.ndarray

        self.apply_config(self.config)

    def apply_config(self, config):
        self.config = replace(config)
        self.position = np.array(self.config.position, dtype=np.float32)
        self.world_up = self._safe_normalize(np.array(self.config.up, dtype=np.float32))

        front = np.array(self.config.target, dtype=np.float32) - self.position
        if np.linalg.norm(front) < 1e-6:
            front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.front = self._safe_normalize(front)
        self._recalculate_basis()

    def process_keyboard(self, movement, step_scale=1.0):
        velocity = float(step_scale) * float(self.config.move_speed)
        if velocity == 0:
            return
        if movement is CameraMovement.FORWARD:
            displacement = self.front * velocity
        elif movement is CameraMovement.BACKWARD:
            displacement = -self.front * velocity
        elif movement is CameraMovement.LEFT:
            displacement = -self.right * velocity
        elif movement is CameraMovement.RIGHT:
            displacement = self.right * velocity
        else:
            return

        self.position = self.position + displacement
        self.config = replace(
            self.config,
            position=tuple(float(v) for v in self.position),
            target=tuple(float(v) for v in (self.position + self.front)),
        )

    def process_mouse(self):
        pass

    def get_view_matrix(self):
        forward = self.front
        right = self.right
        up = self.up
        rotate = np.identity(4, dtype=np.float32)
        rotate[0, 0:3] = right
        rotate[1, 0:3] = up
        rotate[2, 0:3] = -forward
        translate = np.identity(4, dtype=np.float32)
        translate[0:3, 3] = -self.position
        return np.dot(rotate, translate)

    def get_projection_matrix(self):
        fov_rad = np.radians(self.config.fov)
        f = float(1.0 / np.tan(fov_rad / 2.0))
        near = float(self.config.near_plane)
        far = float(self.config.far_plane)

        proj = np.zeros((4, 4), dtype=np.float32)
        proj[0, 0] = f / float(self.aspect_ratio)
        proj[1, 1] = f
        proj[2, 2] = (far + near) / (near - far)
        proj[2, 3] = (2.0 * far * near) / (near - far)
        proj[3, 2] = -1.0
        return proj

    def _recalculate_basis(self):
        self.front = self._safe_normalize(self.front)
        self.right = self._safe_normalize(np.cross(self.front, self.world_up))
        if np.linalg.norm(self.right) < 1e-6:
            self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.up = self._safe_normalize(np.cross(self.right, self.front))
        if np.linalg.norm(self.up) < 1e-6:
            self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    @staticmethod
    def _safe_normalize(vector: np.ndarray):
        norm = float(np.linalg.norm(vector))
        if norm < 1e-6:
            return np.zeros_like(vector)
        return vector / norm


__all__ = ["Camera", "CameraMovement"]
