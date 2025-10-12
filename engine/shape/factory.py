"""Factory helpers for constructing shape instances."""

from __future__ import annotations

from typing import Callable, Dict

from config import ShapeType, ShapeConfig
from config import _SHAPE_VERTEX_PATH, _SHAPE_FRAGMENT_PATH, _LIGHT_FRAGMENT_PATH
from shape import *

FactoryCallback = Callable[[ShapeConfig], Shape]


class ShapeFactory:
    _registry: Dict[ShapeType, FactoryCallback] = {}

    @classmethod
    def create_shape(cls, shape_type: ShapeType, config: ShapeConfig) -> Shape:
        builder = cls._registry.get(shape_type)
        if builder is None:
            raise ValueError(f"Unknown shape type: {shape_type!r}")
        return builder(config)

    @classmethod
    def register_shape(cls, shape_type: ShapeType, builder: FactoryCallback) -> None:
        cls._registry[shape_type] = builder

    @classmethod
    def list_registered_shapes(cls) -> list[ShapeType]:
        return list(cls._registry.keys())


ShapeFactory.register_shape(
    ShapeType.TRIANGLE,
    lambda cfg: Triangle(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.RECTANGLE,
    lambda cfg: Rectangle(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.PENTAGON,
    lambda cfg: Pentagon(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.HEXAGON,
    lambda cfg: Pentagon(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CIRCLE,
    lambda cfg: Circle(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.circle_sector,
    ),
)

ShapeFactory.register_shape(
    ShapeType.ELLIPSE,
    lambda cfg: Ellipse(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.ellipse_sector,
        cfg.ellipse_a,
        cfg.ellipse_b,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRAPEZOID,
    lambda cfg: Trapezoid(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.STAR,
    lambda cfg: Star(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.star_wing,
        cfg.star_outer_radius,
        cfg.star_inner_radius,
    ),
)

ShapeFactory.register_shape(
    ShapeType.ARROW,
    lambda cfg: Arrow(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TETRAHEDRON,
    lambda cfg: Tetrahedron(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CUBE,
    lambda cfg: Cube(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CYLINDER,
    lambda cfg: Cylinder(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.cylinder_sectors,
        cfg.cylinder_height,
        cfg.cylinder_radius,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CONE,
    lambda cfg: Cone(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.cone_height,
        cfg.cone_radius,
        cfg.cone_sectors,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRUNCATED_CONE,
    lambda cfg: TruncatedCone(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.truncated_height,
        cfg.truncated_top_radius,
        cfg.truncated_bottom_radius,
        cfg.truncated_sectors,
    ),
)

ShapeFactory.register_shape(
    ShapeType.SPHERE,
    lambda cfg: Sphere(
        cfg.sphere_radius,
        cfg.sphere_sectors,
        cfg.sphere_stacks,
        cfg.sphere_color,
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TORUS,
    lambda cfg: Torus(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.torus_sectors,
        cfg.torus_stacks,
        cfg.torus_horizontal_radius,
        cfg.torus_vertical_radius,
    ),
)

ShapeFactory.register_shape(
    ShapeType.EQUATION,
    lambda cfg: Equation(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.equation_expression,
        cfg.equation_mesh_size,
        cfg.equation_mesh_density,
    ),
)

ShapeFactory.register_shape(
    ShapeType.MODEL,
    lambda cfg: Model(
        _SHAPE_VERTEX_PATH,
        _SHAPE_FRAGMENT_PATH,
        cfg.model_file,
        cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.LIGHT_SOURCE,
    lambda cfg: LightSource(
        _SHAPE_VERTEX_PATH,
        _LIGHT_FRAGMENT_PATH,
    ),
)


__all__ = ["ShapeFactory"]
