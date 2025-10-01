"""Factory helpers for constructing shape instances."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from config import EngineConfig
from core.enums import ShapeType
from shape import *

FactoryCallback = Callable[[EngineConfig], Shape]


def _shader_path(*parts: str) -> str:
    return str(_SHADER_ROOT.joinpath(*parts).resolve())


_SHADER_ROOT = Path(__file__).resolve().parent.parent
_VERTEX_PATH = _shader_path("graphics", "shape.vert")
_FRAGMENT_PATH = _shader_path("graphics", "shape.frag")


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
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TETRAHEDRON,
    lambda cfg: Tetrahedron(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CUBE,
    lambda cfg: Cube(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CYLINDER,
    lambda cfg: Cylinder(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.cylinder_height,
        cfg.shape_config.cylinder_radius,
        cfg.shape_config.cylinder_sectors,
    ),
)

ShapeFactory.register_shape(
    ShapeType.SPHERE,
    lambda cfg: Sphere(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.sphere_radius,
        cfg.shape_config.sphere_sectors,
        cfg.shape_config.sphere_stacks,
    ),
)


__all__ = ["ShapeFactory"]
