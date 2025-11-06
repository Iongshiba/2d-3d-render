"""Factory helpers for constructing shape instances."""

from __future__ import annotations

from typing import Callable, Dict

from config import ShapeType, ShapeConfig
from config import _SHAPE_VERTEX_PATH, _SHAPE_FRAGMENT_PATH, _LIGHT_FRAGMENT_PATH
from graphics.vertex import Vertex
from shape import *

FactoryCallback = Callable[[ShapeConfig], Shape]


class ShapeFactory:
    _registry: Dict[ShapeType, FactoryCallback] = {}

    @classmethod
    def create_shape(cls, shape_type: ShapeType, config: ShapeConfig) -> Shape:
        builder = cls._registry.get(shape_type)
        return builder(config)

    @classmethod
    def register_shape(cls, shape_type: ShapeType, builder: FactoryCallback) -> None:
        cls._registry[shape_type] = builder

    @classmethod
    def list_registered_shapes(cls) -> list[ShapeType]:
        return list(cls._registry.keys())


def _resolve_color(cfg: ShapeConfig) -> tuple[float | None, float | None, float | None]:
    color = cfg.base_color
    if color is None:
        return (None, None, None)
    return color


def _get_gradient_params(cfg: ShapeConfig):
    """Extract gradient parameters from config."""
    return {
        "gradient_mode": cfg.gradient_mode,
        "gradient_start": cfg.gradient_start_color,
        "gradient_end": cfg.gradient_end_color,
    }


ShapeFactory.register_shape(
    ShapeType.QUICK_DRAW,
    lambda cfg: QuickDraw(
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRIANGLE,
    lambda cfg: Triangle(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.RECTANGLE,
    lambda cfg: Rectangle(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.PENTAGON,
    lambda cfg: Pentagon(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.HEXAGON,
    lambda cfg: Hexagon(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CIRCLE,
    lambda cfg: Circle(
        cfg.circle_sector,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.ELLIPSE,
    lambda cfg: Ellipse(
        cfg.ellipse_sector,
        cfg.ellipse_a,
        cfg.ellipse_b,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRAPEZOID,
    lambda cfg: Trapezoid(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.STAR,
    lambda cfg: Star(
        cfg.star_wing,
        cfg.star_outer_radius,
        cfg.star_inner_radius,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.ARROW,
    lambda cfg: Arrow(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TETRAHEDRON,
    lambda cfg: Tetrahedron(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CUBE,
    lambda cfg: Cube(
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
        **_get_gradient_params(cfg),
    ),
)

ShapeFactory.register_shape(
    ShapeType.CYLINDER,
    lambda cfg: Cylinder(
        cfg.cylinder_sectors,
        cfg.cylinder_height,
        cfg.cylinder_radius,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.CONE,
    lambda cfg: Cone(
        cfg.cone_height,
        cfg.cone_radius,
        cfg.cone_sectors,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.TRUNCATED_CONE,
    lambda cfg: TruncatedCone(
        cfg.truncated_height,
        cfg.truncated_top_radius,
        cfg.truncated_bottom_radius,
        cfg.truncated_sectors,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.SPHERE,
    lambda cfg: Sphere(
        cfg.sphere_radius,
        cfg.sphere_sectors,
        cfg.sphere_stacks,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
        **_get_gradient_params(cfg),
    ),
)

ShapeFactory.register_shape(
    ShapeType.HEART,
    lambda cfg: Heart(
        cfg.heart_sector,
        cfg.heart_stack,
        cfg.heart_scale,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)


ShapeFactory.register_shape(
    ShapeType.TORUS,
    lambda cfg: Torus(
        cfg.torus_sectors,
        cfg.torus_stacks,
        cfg.torus_horizontal_radius,
        cfg.torus_vertical_radius,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.EQUATION,
    lambda cfg: Equation(
        cfg.equation_expression,
        cfg.equation_mesh_size,
        cfg.equation_mesh_density,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.MODEL,
    lambda cfg: Model(
        cfg.model_file,
        color=_resolve_color(cfg),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_SHAPE_FRAGMENT_PATH,
        texture_file=cfg.texture_file,
    ),
)

ShapeFactory.register_shape(
    ShapeType.LIGHT_SOURCE,
    lambda cfg: LightSource(
        color=(1.0, 1.0, 1.0),
        vertex_file=_SHAPE_VERTEX_PATH,
        fragment_file=_LIGHT_FRAGMENT_PATH,
        texture_file=None,
    ),
)


__all__ = ["ShapeFactory"]
