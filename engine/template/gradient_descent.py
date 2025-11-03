from __future__ import annotations

import numpy as np

from config import ShapeConfig, ShapeType
from graphics.scene import Node, TransformNode, GeometryNode, LightNode
from rendering.world import Rotate, Translate, Composite
from shape.factory import ShapeFactory

from . import register_scene


def build_gradient_descent():
    ball_radius = 0.5
    ball_color = (0.698, 0.745, 0.710)
    root = Node()

    equation_cfg = ShapeConfig()
    equation_shape = ShapeFactory.create_shape(ShapeType.EQUATION, equation_cfg)
    equation_node = GeometryNode("surface", equation_shape)
    root.add(equation_node)

    X, Y, Z = equation_shape.get_surface()
    normals = equation_shape.get_normals()
    rows, cols = X.shape
    # Choose random edge: 0=top, 1=bottom, 2=left, 3=right
    edge = np.random.randint(0, 4)
    if edge == 0:  # Top edge
        i, j = 0, np.random.randint(0, cols)
    elif edge == 1:  # Bottom edge
        i, j = rows - 1, np.random.randint(0, cols)
    elif edge == 2:  # Left edge
        i, j = np.random.randint(0, rows), 0
    else:  # Right edge
        i, j = np.random.randint(0, rows), cols - 1
    pos = np.array([X[i, j], Y[i, j], Z[i, j]], dtype=np.float32)
    norm = normals[i, j]
    ball_initial_location = pos + ball_radius * norm

    ball_cfg = ShapeConfig()
    ball_cfg.sphere_radius = ball_radius
    ball_cfg.base_color = ball_color
    ball_shape = ShapeFactory.create_shape(ShapeType.SPHERE, ball_cfg)
    ball_node = GeometryNode("surface", ball_shape)
    ball_spawn = TransformNode(
        "random_place",
        Translate(*ball_initial_location),
        [ball_node],
    )
    root.add(ball_spawn)

    return root


def build() -> Node:
    root = Node("root")

    root.add(build_gradient_descent())

    light_cfg = ShapeConfig()
    light_shape = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, light_cfg)
    light_node = LightNode("preview_light", light_shape)
    light_transform = TransformNode(
        "light_transform", Translate(30.0, 30.0, 30.0), [light_node]
    )
    root.add(light_transform)

    return root


register_scene("gradient_descent", build)
