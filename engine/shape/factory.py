"""Factory helpers for constructing shape instances."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from config import EngineConfig
from config.enums import ShapeType
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
        cfg.shape_config.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.RECTANGLE,
    lambda cfg: Rectangle(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.PENTAGON,
    lambda cfg: Pentagon(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.HEXAGON,
    lambda cfg: Pentagon(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CIRCLE,
    lambda cfg: Circle(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.circle_sector,
    ),
)

ShapeFactory.register_shape(
    ShapeType.ELLIPSE,
    lambda cfg: Ellipse(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.ellipse_sector,
        cfg.shape_config.ellipse_a,
        cfg.shape_config.ellipse_b,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRAPEZOID,
    lambda cfg: Trapezoid(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.STAR,
    lambda cfg: Star(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.star_wing,
        cfg.shape_config.star_outer_radius,
        cfg.shape_config.star_inner_radius,
    ),
)

ShapeFactory.register_shape(
    ShapeType.ARROW,
    lambda cfg: Arrow(
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
        cfg.shape_config.cylinder_sectors,
        cfg.shape_config.cylinder_height,
        cfg.shape_config.cylinder_radius,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CONE,
    lambda cfg: Cone(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.cone_height,
        cfg.shape_config.cone_radius,
        cfg.shape_config.cone_sectors,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRUNCATED_CONE,
    lambda cfg: TruncatedCone(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.truncated_height,
        cfg.shape_config.truncated_top_radius,
        cfg.shape_config.truncated_bottom_radius,
        cfg.shape_config.truncated_sectors,
    ),
)

ShapeFactory.register_shape(
    ShapeType.SPHERE,
    lambda cfg: Sphere(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.texture_file,
        cfg.shape_config.sphere_radius,
        cfg.shape_config.sphere_sectors,
        cfg.shape_config.sphere_stacks,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TORUS,
    lambda cfg: Torus(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.torus_sectors,
        cfg.shape_config.torus_stacks,
        cfg.shape_config.torus_horizontal_radius,
        cfg.shape_config.torus_vertical_radius,
    ),
)

ShapeFactory.register_shape(
    ShapeType.EQUATION,
    lambda cfg: Equation(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.equation_expression,
        cfg.shape_config.equation_mesh_size,
        cfg.shape_config.equation_mesh_density,
    ),
)

ShapeFactory.register_shape(
    ShapeType.MODEL,
    lambda cfg: Model(
        _VERTEX_PATH,
        _FRAGMENT_PATH,
        cfg.shape_config.model_file,
        cfg.shape_config.texture_file,
    ),
)

__all__ = ["ShapeFactory"]
