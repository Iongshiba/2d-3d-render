"""Rendering strategies implementing the strategy pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from OpenGL import GL

from ...config import EngineConfig


class RenderingStrategy(ABC):
    """Define the interface for rendering strategies."""

    @abstractmethod
    def setup_gl_state(self, config: EngineConfig) -> None:
        """Configure global OpenGL state prior to drawing."""

    @abstractmethod
    def apply_to_shape(self, shape: Any) -> None:
        """Apply shape specific state before drawing."""


class FillRenderingStrategy(RenderingStrategy):
    def setup_gl_state(self, config: EngineConfig) -> None:
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

    def apply_to_shape(self, shape: Any) -> None:  # noqa: D401 - simple hook
        """No-op for fill mode."""


class WireframeRenderingStrategy(RenderingStrategy):
    def setup_gl_state(self, config: EngineConfig) -> None:
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

    def apply_to_shape(self, shape: Any) -> None:  # noqa: D401 - simple hook
        """No-op for wireframe mode."""


__all__ = [
    "RenderingStrategy",
    "FillRenderingStrategy",
    "WireframeRenderingStrategy",
]
