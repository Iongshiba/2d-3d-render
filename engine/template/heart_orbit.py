"""Heart orbit scene with a textured rectangle center and orbiting hearts."""

from __future__ import annotations

import numpy as np

from config import ShapeConfig, ShapeType
from graphics.scene import GeometryNode, LightNode, Node, TransformNode
from rendering.world import Rotate, Translate
from shape import ShapeFactory, Heart, Rectangle

from rendering.animation import circular_orbit


shape_cfg = ShapeConfig()


def _generate_center_rectangle():
    """Generate a textured rectangle at the center, standing upright."""
    texture_path = r"C:\Users\Admin\Documents\long\document\college\hk251\computer_graphics\assignment1\engine\textures\then.png"
    return TransformNode(
        "center_rectangle",
        Translate(0.0, 0.0, 0.0),
        [
            TransformNode(
                "rectangle_rotation",
                Rotate(axis=(1.0, 0.0, 0.0), angle=90.0),
                [
                    TransformNode(
                        "rectangle_rotation",
                        Rotate(axis=(0.0, 0.0, 1.0), angle=90),
                        [
                            GeometryNode(
                                "rectangle", Rectangle(texture_file=texture_path)
                            )
                        ],
                    )
                ],
            )
        ],
    )


def _generate_orbiting_heart(phase, radius, speed):
    """Generate a heart that orbits around the center."""
    color = (1.0, 0.2, 0.4)  # Pink/red color for hearts
    return TransformNode(
        "heart",
        Translate(0.0, 0.0, 0.0, circular_orbit(phase, speed, radius, axis="xy")),
        [GeometryNode("heart", Heart(sector=64, stack=32, scale=0.5, color=color))],
    )


def build() -> Node:
    """Build the heart orbit scene."""
    scene = Node("heart_orbit_root")

    # Add center rectangle with texture
    scene.add(_generate_center_rectangle())

    # Add 4 orbiting hearts at different phases (90 degrees apart)
    orbit_radius = 5.0
    orbit_speed = 0.8

    for i in range(1):
        phase = i * np.pi / 2  # 0, π/2, π, 3π/2
        heart = _generate_orbiting_heart(phase, orbit_radius, orbit_speed)
        scene.add(heart)

    # Add light source
    light = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, shape_cfg)
    scene.add(
        TransformNode(
            "light_parent",
            Translate(30.0, 30.0, 30.0),
            [LightNode("light", light)],
        )
    )

    return scene


from . import register_scene

# register_scene("heart_orbit", build)
