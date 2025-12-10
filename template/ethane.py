"""Preset scene for ethane (C2H6) approximate ball-and-stick model."""

from __future__ import annotations

import numpy as np
from graphics.scene import Node, TransformNode, GeometryNode
from rendering.world import Translate, Rotate
from shape.factory import ShapeFactory
from config import ShapeConfig, ShapeType

from .molecule import generate_molecule
from . import register_scene


def build() -> Node:
    # Represent ethane roughly as two carbons with three hydrogens each
    root = Node("ethane_root")
    # Left carbon
    left = generate_molecule(
        centroid=(-2.0, 0.0, 0.0),
        attached_count=3,
        bond_length=3.5,
        radii=(1.8, 0.9),
        bond_radius=0.12,
        core_color=(0.2, 0.2, 0.2),
        shell_color=(0.95, 0.95, 0.95),
    )
    # Right carbon
    right = generate_molecule(
        centroid=(2.0, 0.0, 0.0),
        attached_count=3,
        bond_length=3.5,
        radii=(1.8, 0.9),
        bond_radius=0.12,
        core_color=(0.2, 0.2, 0.2),
        shell_color=(0.95, 0.95, 0.95),
    )
    root.add(left)
    root.add(right)

    # Add C-C bond between the two carbons
    cfg = ShapeConfig()
    cfg.cylinder_height = 4.0
    cfg.cylinder_radius = 0.15
    cfg.base_color = (0.7, 0.7, 0.7)
    bond = ShapeFactory.create_shape(ShapeType.CYLINDER, cfg)
    bond_node = GeometryNode("c_c_bond", bond)
    root.add(
        TransformNode(
            "c_c_bond_transform",
            Rotate(axis=(0, 1, 0), angle=90),
            [bond_node],
        )
    )

    return root


register_scene("ethane", build)
