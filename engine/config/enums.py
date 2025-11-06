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
    HEXAGON = auto()
    CIRCLE = auto()
    ELLIPSE = auto()
    TRAPEZOID = auto()
    STAR = auto()
    ARROW = auto()
    CUBE = auto()
    SPHERE = auto()
    HEART = auto()
    CYLINDER = auto()
    CONE = auto()              
    TRUNCATED_CONE = auto()    
    TETRAHEDRON = auto()
    TORUS = auto()
    QUICK_DRAW = auto()     
    EQUATION = auto()
    MODEL = auto()
    LIGHT_SOURCE = auto()


class ColorMode(Enum):
    FLAT = 0
    VERTEX = 1


class ShadingModel(Enum):
    NORMAL = 0
    PHONG = 1


class TextureMode(Enum):
    NONE = 0
    ENABLED = 1


class RenderMode(Enum):
    FILL = 0
    WIREFRAME = 1


class GradientMode(Enum):
    NONE = 0
    LINEAR_X = 1  # Gradient along X axis
    LINEAR_Y = 2  # Gradient along Y axis
    LINEAR_Z = 3  # Gradient along Z axis
    RADIAL = 4  # Gradient from center
    DIAGONAL = 5  # Gradient along diagonal
    RAINBOW = 6  # Rainbow gradient
