from __future__ import annotations

from dataclasses import replace

import numpy as np

from config import CameraConfig
from core.enums import CameraMovement


class Camera:
    def __init__(self, config=None):
        self.aspect_ratio = 1.0
        self.world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        # Internal state vectors
        self.position = np.array(config.position, dtype=np.float32)
        self.front = np.array(config.front, dtype=np.float32)
        self.up = np.array(config.up, dtype=np.float32)
        self.right = np.array(config.right, dtype=np.float32)
        self.yaw = np.float32(config.yaw)
        self.pitch = np.float32(config.pitch)

        self.fov = np.float32(config.fov)
        self.near_plane = np.float32(config.near_plane)
        self.far_plane = np.float32(config.far_plane)
        self.move_speed = np.float32(config.move_speed)
        self.sensitivity = np.float32(config.sensitivity)

    def process_keyboard(self, movement, step_scale=1.0):
        velocity = float(step_scale) * float(self.move_speed)
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
        self._recalculate_basis()

    def process_mouse(self, offset=(0.0, 0.0)):
        yaw_offset = np.float32(offset[0]) * self.sensitivity
        pitch_offset = np.float32(offset[1]) * self.sensitivity
        if yaw_offset == 0 and pitch_offset == 0:
            return
        self.yaw += -yaw_offset
        self.pitch += pitch_offset

        # Clamp pitch to avoid flipping
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        cp = np.cos(np.radians(self.pitch))
        cy = np.cos(np.radians(self.yaw))
        sp = np.sin(np.radians(self.pitch))
        sy = np.sin(np.radians(self.yaw))

        # Imagine the camera rotation as a sphere
        self.front = np.array(
            [
                cp * cy,
                sp,
                cp * sy,
            ],
            dtype=np.float32,
        )
        self._recalculate_basis()

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
        fov_rad = np.radians(self.fov)
        f = float(1.0 / np.tan(fov_rad / 2.0))
        near = float(self.near_plane)
        far = float(self.far_plane)

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
