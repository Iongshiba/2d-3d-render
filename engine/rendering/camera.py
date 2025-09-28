from __future__ import annotations

from dataclasses import asdict, replace
from typing import Iterable

import numpy as np

from config import CameraConfig
from core.enums import CameraMovement


class Camera:
    """Simple FPS-style camera supporting positional movement."""

    def __init__(self, config: CameraConfig | None = None) -> None:
        self.config = CameraConfig() if config is None else replace(config)
        self.aspect_ratio: float = 1.0

        # Internal state vectors
        self.position: np.ndarray
        self.front: np.ndarray
        self.world_up: np.ndarray
        self.right: np.ndarray
        self.up: np.ndarray

        self.apply_config(self.config)

    def apply_config(self, config: CameraConfig) -> None:
        """Apply a fresh camera configuration."""

        self.config = replace(config)
        self.position = np.array(self.config.position, dtype=np.float32)
        self.world_up = self._safe_normalize(np.array(self.config.up, dtype=np.float32))

        front = np.array(self.config.target, dtype=np.float32) - self.position
        if np.linalg.norm(front) < 1e-6:
            front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.front = self._safe_normalize(front)
        self._recalculate_basis()

    def process_keyboard(
        self, movement: CameraMovement, step_scale: float = 1.0
    ) -> None:
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

    def get_view_matrix(self) -> np.ndarray:
        forward = self.front
        right = self.right
        up = self.up

        view = np.identity(4, dtype=np.float32)
        view[0, 0:3] = right
        view[1, 0:3] = up
        view[2, 0:3] = -forward

        view[0, 3] = -np.dot(right, self.position)
        view[1, 3] = -np.dot(up, self.position)
        view[2, 3] = np.dot(forward, self.position)
        return view

    def get_projection_matrix(self) -> np.ndarray:
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

    def apply_to_shape(self, shape, aspect_ratio: float | None = None) -> None:
        if aspect_ratio is not None:
            self.aspect_ratio = aspect_ratio

        view = self.get_view_matrix()
        projection = self.get_projection_matrix()

        if hasattr(shape, "set_camera_matrices"):
            shape.set_camera_matrices(view, projection)
        else:
            shape.lookat(
                self.position.tolist(),
                (self.position + self.front).tolist(),
                self.up.tolist(),
            )
            shape.project(
                fov=self.config.fov,
                aspect_ratio=self.aspect_ratio,
                near=self.config.near_plane,
                far=self.config.far_plane,
            )

    def _recalculate_basis(self) -> None:
        self.front = self._safe_normalize(self.front)
        self.right = self._safe_normalize(np.cross(self.front, self.world_up))
        if np.linalg.norm(self.right) < 1e-6:
            self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.up = self._safe_normalize(np.cross(self.right, self.front))
        if np.linalg.norm(self.up) < 1e-6:
            self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    @staticmethod
    def _safe_normalize(vector: np.ndarray) -> np.ndarray:
        norm = float(np.linalg.norm(vector))
        if norm < 1e-6:
            return np.zeros_like(vector)
        return vector / norm


__all__ = ["Camera", "CameraMovement"]
