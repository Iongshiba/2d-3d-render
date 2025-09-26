"""Backward-compatible exports for configuration and enums."""

from __future__ import annotations

from ..config import EngineConfig, ShapeConfig
from .enums import ColorMode, RenderMode, ShadingModel, ShapeType, TextureMode


__all__ = [
    "EngineConfig",
    "ShapeConfig",
    "ShapeType",
    "ColorMode",
    "ShadingModel",
    "TextureMode",
    "RenderMode",
]
