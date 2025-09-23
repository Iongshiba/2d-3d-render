from dataclasses import dataclass
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
    PHONG = 1  # placeholder


class TextureMode(Enum):
    NONE = 0
    ENABLED = 1  # placeholder


class RenderMode(Enum):
    FILL = 0
    WIREFRAME = 1  # placeholder


@dataclass
class EngineConfig:
    width: int = 1000
    height: int = 1000
    shape: ShapeType = ShapeType.SPHERE
    color_mode: ColorMode = ColorMode.VERTEX
    shading: ShadingModel = ShadingModel.NONE
    texture: TextureMode = TextureMode.NONE
    render_mode: RenderMode = RenderMode.FILL
    flat_color: tuple[float, float, float] | list[float] = (0.8, 0.2, 0.9)

    # Shape-specific params (optional, hardcoded for now)
    cylinder_height: float = 1.0
    cylinder_radius: float = 0.5
    cylinder_sectors: int = 20

    sphere_radius: float = 2.0
    sphere_sectors: int = 160
    sphere_stacks: int = 161
