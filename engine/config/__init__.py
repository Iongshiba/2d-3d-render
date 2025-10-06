"""Engine configuration dataclasses and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Tuple

from config.enums import (
    ColorMode,
    RenderMode,
    ShadingModel,
    ShapeType,
    TextureMode,
)

RGBColor = Tuple[float, float, float]


@dataclass(slots=True)
class ShapeConfig:
    """Shape specific configuration attributes."""

    cylinder_height: float = 1.0
    cylinder_radius: float = 0.5
    cylinder_sectors: int = 20

    sphere_radius: float = 2.0
    sphere_sectors: int = 40
    # TODO handle any sphere_stacks
    sphere_stacks: int = 41

    circle_sector: int = 100

    ellipse_sector: int = 100
    ellipse_a: int = 3
    ellipse_b: int = 1

    star_wing: int = 5
    star_outer_radius: int = 2
    star_inner_radius: int = 1

    cone_height: float = 1.0
    cone_radius: float = 0.5
    cone_sectors: int = 20

    truncated_height: float = 1.0
    truncated_top_radius: float = 0.3
    truncated_bottom_radius: float = 0.5
    truncated_sectors: int = 20

    torus_sectors: int = 50
    torus_stacks: int = 50
    torus_horizontal_radius: float = 10.0
    torus_vertical_radius: float = 5.0

    equation_expression: str = "x + y"
    equation_mesh_size: int = 10
    equation_mesh_density: int = 100

    texture_file: str = ""


@dataclass(slots=True)
class CameraConfig:
    """Camera configuration parameters for initial setup."""

    position: Tuple[float, float, float] = (0.0, 0.0, 5.0)
    # target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    front: Tuple[float, float, float] = (0.0, 0.0, -1.0)
    up: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    right: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    fov: float = 75.0
    near_plane: float = 0.1
    far_plane: float = 100.0
    move_speed: float = 0.25
    yaw: float = -90.0
    pitch: float = 0.0
    sensitivity: float = 0.05


@dataclass(slots=True)
class TrackballConfig:
    """Trackball configuration parameters for initial setup."""

    yaw: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    distance: float = 10.0
    radians: bool = None
    pan_sensitivity: float = 0.001


@dataclass(slots=True)
class EngineConfig:
    """Aggregated configuration for the rendering engine."""

    width: int = 1000
    height: int = 1000
    shape: ShapeType = ShapeType.SPHERE
    shape_config: ShapeConfig = field(default_factory=ShapeConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    trackball: TrackballConfig = field(default_factory=TrackballConfig)
    cull_face: bool = (
        True
        if shape
        in [
            ShapeType.TRIANGLE,
            ShapeType.RECTANGLE,
            ShapeType.PENTAGON,
            ShapeType.HEXAGON,
            ShapeType.CIRCLE,
            ShapeType.ELLIPSE,
            ShapeType.TRAPEZOID,
            ShapeType.STAR,
            ShapeType.ARROW,
            ShapeType.EQUATION,
        ]
        else False
    )

    @classmethod
    def from_dict(cls, config_dict: Mapping[str, Any]) -> "EngineConfig":
        """Create a configuration instance from a nested mapping."""

        data: MutableMapping[str, Any] = dict(config_dict)
        shape_values = data.pop("shape_config", {})
        shape_config = (
            shape_values
            if isinstance(shape_values, ShapeConfig)
            else ShapeConfig(**shape_values)
        )
        camera_values = data.pop("camera", {})
        camera_config = (
            camera_values
            if isinstance(camera_values, CameraConfig)
            else CameraConfig(**camera_values)
        )
        return cls(shape_config=shape_config, camera=camera_config, **data)

    def update(self, updates: Mapping[str, Any]) -> None:
        """Update configuration fields from a mapping."""

        for key, value in updates.items():
            if key == "shape_config":
                if isinstance(value, Mapping):
                    for attr, nested_value in value.items():
                        setattr(self.shape_config, attr, nested_value)
                elif isinstance(value, ShapeConfig):
                    self.shape_config = value
                else:
                    raise TypeError("shape_config must be mapping or ShapeConfig")
            elif key == "camera":
                if isinstance(value, Mapping):
                    for attr, nested_value in value.items():
                        setattr(self.camera, attr, nested_value)
                elif isinstance(value, CameraConfig):
                    self.camera = value
                else:
                    raise TypeError("camera must be mapping or CameraConfig")
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Unknown configuration field: {key}")

    def __getattr__(self, item: str) -> Any:
        """Provide backward-compatible access to shape configuration fields."""

        if hasattr(self.shape_config, item):
            return getattr(self.shape_config, item)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {item!r}")


__all__ = ["EngineConfig", "ShapeConfig", "CameraConfig", "RGBColor"]
