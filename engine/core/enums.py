"""Core enumerations for engine configuration and rendering options."""

from __future__ import annotations

from enum import Enum, auto


class ShapeType(Enum):
    TRIANGLE = auto()
    CUBE = auto()
    CYLINDER = auto()
    SPHERE = auto()


class ColorMode(Enum):
    FLAT = 0
    VERTEX = 1


class ShadingModel(Enum):
    NONE = 0
    PHONG = 1


class TextureMode(Enum):
    NONE = 0
    ENABLED = 1


class RenderMode(Enum):
    FILL = 0
    WIREFRAME = 1


__all__ = [
    "ShapeType",
    "ColorMode",
    "ShadingModel",
    "TextureMode",
    "RenderMode",
]
