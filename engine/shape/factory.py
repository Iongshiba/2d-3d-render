"""Factory helpers for constructing shape instances."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from config import EngineConfig
from core.enums import ShapeType
from .base import Shape
from .cube.cube import Cube
from .cylinder.cylinder import Cylinder
from .sphere.sphere import Sphere
from .triangle.triangle import Triangle

FactoryCallback = Callable[[EngineConfig], Shape]

_SHADER_ROOT = Path(__file__).resolve().parent


def _shader_path(*parts: str) -> str:
    return str(_SHADER_ROOT.joinpath(*parts).resolve())


class ShapeFactory:
    _registry: Dict[ShapeType, FactoryCallback] = {}

    @classmethod
    def create_shape(cls, shape_type: ShapeType, config: EngineConfig) -> Shape:
        builder = cls._registry.get(shape_type)
        if builder is None:
            raise ValueError(f"Unknown shape type: {shape_type!r}")
        return builder(config)

    @classmethod
    def register_shape(cls, shape_type: ShapeType, builder: FactoryCallback) -> None:
        cls._registry[shape_type] = builder


ShapeFactory.register_shape(
    ShapeType.TRIANGLE,
    lambda cfg: Triangle(
        _shader_path("triangle", "triangle.vert"),
        _shader_path("triangle", "triangle.frag"),
    ),
)

ShapeFactory.register_shape(
    ShapeType.CUBE,
    lambda cfg: Cube(
        _shader_path("cube", "cube.vert"),
        _shader_path("cube", "cube.frag"),
    ),
)

ShapeFactory.register_shape(
    ShapeType.CYLINDER,
    lambda cfg: Cylinder(
        _shader_path("cylinder", "cylinder.vert"),
        _shader_path("cylinder", "cylinder.frag"),
        cfg.shape_config.cylinder_height,
        cfg.shape_config.cylinder_radius,
        cfg.shape_config.cylinder_sectors,
    ),
)

ShapeFactory.register_shape(
    ShapeType.SPHERE,
    lambda cfg: Sphere(
        _shader_path("sphere", "sphere.vert"),
        _shader_path("sphere", "sphere.frag"),
        cfg.shape_config.sphere_radius,
        cfg.shape_config.sphere_sectors,
        cfg.shape_config.sphere_stacks,
    ),
)


__all__ = ["ShapeFactory"]
