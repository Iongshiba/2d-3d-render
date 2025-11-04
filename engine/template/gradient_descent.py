from __future__ import annotations

import numpy as np

from config import ShapeConfig, ShapeType
from graphics.scene import Node, TransformNode, GeometryNode, LightNode
from rendering.world import Rotate, Translate, Composite
from rendering.animation import gradient_descent
from shape.factory import ShapeFactory

from . import register_scene


def build_gradient_descent():
    ball_radius = 0.2
    ball_color = (0.698, 0.745, 0.710)
    equation_str = "(x^2 + y^2)"
    equation_str = "(x^2 + y - 11)^2 + (x + y^2 - 7)^2"

    root = Node()

    equation_cfg = ShapeConfig()
    equation_cfg.equation_expression = equation_str
    # Set to a uniform color to see Phong shading clearly
    equation_cfg.base_color = (0.8, 0.8, 0.9)  # Light blue-gray
    equation_shape = ShapeFactory.create_shape(ShapeType.EQUATION, equation_cfg)
    equation_node = GeometryNode("surface", equation_shape)
    root.add(equation_node)

    X, Y, Z = equation_shape.surface
    normals = equation_shape.normals
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

    # Create gradient descent animation
    gd_animation = gradient_descent(equation=equation_shape, ball_radius=ball_radius)

    ball_cfg = ShapeConfig()
    ball_cfg.sphere_radius = ball_radius
    ball_cfg.base_color = ball_color
    ball_shape = ShapeFactory.create_shape(ShapeType.SPHERE, ball_cfg)
    ball_node = GeometryNode("ball", ball_shape)
    ball_spawn = TransformNode(
        "ball_transform",
        Translate(*ball_initial_location, animate=gd_animation),
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
        "light_transform", Translate(0.0, 30.0, 30.0), [light_node]
    )
    root.add(light_transform)

    return root


register_scene("gradient_descent", build)
