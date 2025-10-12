"""Original atom-inspired scene packaged as a builder."""

from __future__ import annotations

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


def _generate_electron(radius, speed):
    color = (0.2, 0.2, 0.8)
    return TransformNode(
        "electron",
        Translate(0.0, radius, 0.0, circular_orbit(speed, radius, axis="xz")),
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
    scene.add(_generate_nucleus(0, 0, 0, 1, 6, 3))

    for idx, radius in enumerate((5.0, 10.0, 15.0)):
        ring = _generate_orbit_ring(radius)
        electron = _generate_electron(radius, speed=1.0 + idx * 0.2)
        scene.add(ring)
        scene.add(electron)

    shape_cfg.sphere_color = (1.0, 1.0, 1.0)
    light = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, shape_cfg)
    scene.add(
        TransformNode(
            "light_parent",
            Translate(15.0, 15.0, 15.0),
            [LightNode("light", light)],
        )
    )

    return scene


from . import register_scene

register_scene("atom", build)
