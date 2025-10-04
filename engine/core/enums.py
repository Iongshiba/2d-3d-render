"""Core enumerations for engine configuration and rendering options."""

from __future__ import annotations

from enum import Enum, auto


class CameraMovement(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()


class ShapeType(Enum):
    # fmt: off
    TRIANGLE = auto()
    RECTANGLE = auto()
    PENTAGON = auto()           
    HEXAGON = auto()    #TODO
    CIRCLE = auto()             #TODO
    ELLIPSE = auto()            #TODO
    TRAPEZOID = auto()          #TODO
    STAR = auto()               #TODO
    ARROW = auto()              #TODO
    CUBE = auto()
    SPHERE = auto()
    CYLINDER = auto()
    CONE = auto()               #TODO
    TRUNCATED_CONE = auto()     #TODO
    TETRAHEDRON = auto()
    TORUS = auto()              #TODO
    PRISM = auto()              #TODO


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
    "CameraMovement",
    "ShapeType",
    "ColorMode",
    "ShadingModel",
    "TextureMode",
    "RenderMode",
]
