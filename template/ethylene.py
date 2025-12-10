"""Preset scene for ethylene (C2H4) approximate ball-and-stick model."""

from __future__ import annotations

from graphics.scene import Node, TransformNode, GeometryNode
from rendering.world import Translate, Rotate
from shape.factory import ShapeFactory
from config import ShapeConfig, ShapeType

from .molecule import generate_molecule
from . import register_scene


def build() -> Node:
    # Approximate ethylene as two carbons each with two hydrogens
    root = Node("ethylene_root")
    left = generate_molecule(
        centroid=(-2.0, 0.0, 0.0),
        attached_count=2,
        bond_length=3.6,
        radii=(1.8, 0.9),
        bond_radius=0.12,
        core_color=(0.2, 0.2, 0.2),
        shell_color=(0.95, 0.95, 0.95),
    )
    right = generate_molecule(
        centroid=(2.0, 0.0, 0.0),
        attached_count=2,
        bond_length=3.6,
        radii=(1.8, 0.9),
        bond_radius=0.12,
        core_color=(0.2, 0.2, 0.2),
        shell_color=(0.95, 0.95, 0.95),
    )
    root.add(left)
    root.add(right)

    # Add C=C double bond between the two carbons (represented as two parallel bonds)
    for i, offset_y in enumerate([0.2, -0.2]):
        cfg = ShapeConfig()
        cfg.cylinder_height = 4.0
        cfg.cylinder_radius = 0.12
        cfg.base_color = (0.7, 0.7, 0.7)
        bond = ShapeFactory.create_shape(ShapeType.CYLINDER, cfg)
        bond_node = GeometryNode(f"c_c_bond_{i}", bond)
        root.add(
            TransformNode(
                f"c_c_bond_transform_{i}",
                Translate(0.0, offset_y, 0.0),
                [
                    TransformNode(
                        f"c_c_bond_rotate_{i}",
                        Rotate(axis=(0, 1, 0), angle=90),
                        [bond_node],
                    )
                ],
            )
        )

    return root


register_scene("ethylene", build)
