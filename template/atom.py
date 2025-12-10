"""Original atom-inspired scene packaged as a builder."""

from __future__ import annotations

import math
import numpy as np

from config import ShapeConfig, ShapeType
from graphics.scene import GeometryNode, LightNode, Node, TransformNode
from rendering.world import Rotate, Translate
from shape import ShapeFactory, Ring, Sphere

from rendering.animation import circular_orbit


shape_cfg = ShapeConfig()


def _generate_nucleus(x, y, z, radius, sector, stack):
    stacks = np.linspace(-np.pi / 2, np.pi / 2, stack)
    sectors = np.linspace(0, 2 * np.pi, sector)
    proton_color = (0.8, 0.2, 0.2)
    neutron_color = (0.0, 0.8, 0.0)
    color = neutron_color

    atom_sphere = []
    for stack in stacks:
        for sector in sectors:
            color = proton_color if color == neutron_color else neutron_color
            atom_sphere.append(
                TransformNode(
                    "atom_sphere",
                    Translate(
                        radius * np.cos(stack) * np.cos(sector),
                        radius * np.cos(stack) * np.sin(sector),
                        radius * np.sin(stack),
                    ),
                    [GeometryNode("atom", Sphere(1, 20, 20, color))],
                )
            )

    return TransformNode("nucleus", Translate(x, y, z), atom_sphere)


def _generate_electron(phase, radius, speed):
    color = (0.2, 0.2, 0.8)
    return TransformNode(
        "electron",
        Translate(0.0, 0.0, 0.0, circular_orbit(phase, speed, radius, axis="xz")),
        [GeometryNode("electron", Sphere(0.8, 20, 20, color))],
    )


def _generate_orbit_ring(radius):
    color = (0.8, 0.8, 0.8)
    return TransformNode(
        "ring",
        Rotate(axis=(1.0, 0.0, 0.0), angle=90.0),
        [GeometryNode("ring", Ring(radius, 50, color))],
    )


def build() -> Node:
    scene = Node("atom_root")
    scene.add(_generate_nucleus(0, 0, 0, 1, 7, 4))

    electron_meta = [
        *[(phase, 4.0, 0.5) for phase in np.linspace(0, np.pi * 2, 3)],
        *[(phase, 8.0, 0.6) for phase in np.linspace(0, np.pi * 2, 10)],
        *[(phase, 12.0, 0.7) for phase in np.linspace(0, np.pi * 2, 18)],
        *[(phase, 16.0, 0.8) for phase in np.linspace(0, np.pi * 2, 32)],
        # *[(phase, 20.0, 0.9) for phase in np.linspace(0, np.pi * 2, 50)],
        # *[(phase, 24.0, 0.8) for phase in np.linspace(0, np.pi * 2, 72)],
        # *[(phase, 28.0, 0.8) for phase in np.linspace(0, np.pi * 2, 98)],
    ]

    for phase, radius, speed in electron_meta:
        ring = _generate_orbit_ring(radius)
        electron = _generate_electron(phase, radius, speed)
        scene.add(ring)
        scene.add(electron)

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

register_scene("atom", build)
