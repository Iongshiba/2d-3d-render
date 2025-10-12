from __future__ import annotations

from dataclasses import replace

from config import ShapeConfig, ShapeType
from graphics.scene import GeometryNode, LightNode, Node, TransformNode
from rendering.world import Rotate, Scale, Translate
from shape.factory import ShapeFactory


TWO_D_SHAPES: set[ShapeType] = {
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
}

THREE_D_SHAPES: set[ShapeType] = {
    ShapeType.CUBE,
    ShapeType.SPHERE,
    ShapeType.CYLINDER,
    ShapeType.CONE,
    ShapeType.TRUNCATED_CONE,
    ShapeType.TETRAHEDRON,
    ShapeType.TORUS,
    ShapeType.MODEL,
}


def is_2d_shape(shape_type: ShapeType) -> bool:
    return shape_type in TWO_D_SHAPES


def is_3d_shape(shape_type: ShapeType) -> bool:
    return shape_type in THREE_D_SHAPES


def build_shape_scene(shape_type: ShapeType, config: ShapeConfig | None = None) -> Node:
    """Create a standalone scene for a single shape with a default light."""

    if shape_type is ShapeType.LIGHT_SOURCE:
        raise ValueError(
            "Light source is reserved for lighting and cannot be previewed as a standalone scene."
        )

    # Copy incoming configuration so UI interactions do not mutate shared state.
    shape_cfg = replace(config) if config is not None else ShapeConfig()
    shape = ShapeFactory.create_shape(shape_type, shape_cfg)

    root = Node(f"{shape_type.name.lower()}_scene")

    geometry_node = GeometryNode(f"{shape_type.name.lower()}_geometry", shape)
    # Slight rotation and scaling give the trackball something to work with by default.
    model = TransformNode(
        "model_transform",
        Scale(1.0, 1.0, 1.0),
        [
            TransformNode(
                "model_rotation",
                Rotate(axis=(0.0, 1.0, 0.0), angle=0.0),
                [geometry_node],
            )
        ],
    )
    root.add(model)

    light_cfg = ShapeConfig()
    light_shape = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, light_cfg)
    light_node = LightNode("preview_light", light_shape)
    light_transform = TransformNode(
        "light_transform",
        Translate(6.0, 6.0, 6.0),
        [light_node],
    )
    root.add(light_transform)

    return root
