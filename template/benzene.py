"""Preset scene for benzene (C6H6) hexagonal ring molecule."""

from __future__ import annotations

import math
from graphics.scene import Node, TransformNode, GeometryNode, LightNode
from rendering.world import Translate, Rotate, Composite
from shape.factory import ShapeFactory
from config import ShapeConfig, ShapeType
from . import register_scene


def build() -> Node:
    root = Node("benzene_root")

    # Create 6 carbon atoms in a hexagonal ring
    ring_radius = 4.0
    carbon_radius = 1.5
    h_radius = 0.8
    bond_radius = 0.15
    bond_length = 3.5

    # Carbon atoms at hexagon vertices
    carbon_positions = []
    for i in range(6):
        angle = math.pi / 6 + 2 * math.pi * i / 6  # Start at 30 degrees
        x = ring_radius * math.cos(angle)
        y = ring_radius * math.sin(angle)
        carbon_positions.append((x, y, 0.0))

    # Add carbon atoms
    for i, pos in enumerate(carbon_positions):
        cfg = ShapeConfig()
        cfg.sphere_radius = carbon_radius
        cfg.base_color = (0.2, 0.2, 0.2)
        carbon = ShapeFactory.create_shape(ShapeType.SPHERE, cfg)
        root.add(
            TransformNode(
                f"carbon_{i}",
                Translate(*pos),
                [GeometryNode(f"carbon_{i}_geo", carbon)],
            )
        )

    # Add C-C bonds between adjacent carbons (alternating single/double bonds)
    for i in range(6):
        next_i = (i + 1) % 6
        pos1 = carbon_positions[i]
        pos2 = carbon_positions[next_i]

        # Calculate midpoint and direction
        mid_x = (pos1[0] + pos2[0]) / 2
        mid_y = (pos1[1] + pos2[1]) / 2
        mid_z = 0.0

        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        length = math.sqrt(dx * dx + dy * dy)
        angle_deg = math.degrees(math.atan2(dy, dx))

        # Alternating single and double bonds for aromatic representation
        if i % 2 == 0:  # Double bond
            for j, offset_z in enumerate([0.15, -0.15]):
                cfg = ShapeConfig()
                cfg.cylinder_height = length
                cfg.cylinder_radius = bond_radius * 0.8
                cfg.base_color = (0.6, 0.6, 0.6)
                bond = ShapeFactory.create_shape(ShapeType.CYLINDER, cfg)
                root.add(
                    TransformNode(
                        f"bond_{i}_{j}",
                        Translate(mid_x, mid_y, offset_z),
                        [
                            TransformNode(
                                f"bond_{i}_{j}_rot",
                                Composite(
                                    [
                                        Rotate(axis=(0, 0, 1), angle=angle_deg),
                                        Rotate(axis=(0, 1, 0), angle=90),
                                    ]
                                ),
                                [GeometryNode(f"bond_{i}_{j}_geo", bond)],
                            )
                        ],
                    )
                )
        else:  # Single bond
            cfg = ShapeConfig()
            cfg.cylinder_height = length
            cfg.cylinder_radius = bond_radius
            cfg.base_color = (0.7, 0.7, 0.7)
            bond = ShapeFactory.create_shape(ShapeType.CYLINDER, cfg)
            root.add(
                TransformNode(
                    f"bond_{i}",
                    Translate(mid_x, mid_y, mid_z),
                    [
                        TransformNode(
                            f"bond_{i}_rot",
                            Composite(
                                [
                                    Rotate(axis=(0, 0, 1), angle=angle_deg),
                                    Rotate(axis=(0, 1, 0), angle=90),
                                ]
                            ),
                            [GeometryNode(f"bond_{i}_geo", bond)],
                        )
                    ],
                )
            )

    # Add hydrogen atoms (one per carbon, pointing outward)
    for i, pos in enumerate(carbon_positions):
        angle = math.pi / 6 + 2 * math.pi * i / 6
        h_distance = ring_radius + bond_length
        h_x = h_distance * math.cos(angle)
        h_y = h_distance * math.sin(angle)

        # Hydrogen atom
        cfg = ShapeConfig()
        cfg.sphere_radius = h_radius
        cfg.base_color = (0.9, 0.9, 0.9)
        hydrogen = ShapeFactory.create_shape(ShapeType.SPHERE, cfg)
        root.add(
            TransformNode(
                f"hydrogen_{i}",
                Translate(h_x, h_y, 0.0),
                [GeometryNode(f"hydrogen_{i}_geo", hydrogen)],
            )
        )

        # C-H bond
        mid_x = (pos[0] + h_x) / 2
        mid_y = (pos[1] + h_y) / 2
        dx = h_x - pos[0]
        dy = h_y - pos[1]
        ch_length = math.sqrt(dx * dx + dy * dy)
        ch_angle = math.degrees(math.atan2(dy, dx))

        cfg = ShapeConfig()
        cfg.cylinder_height = ch_length
        cfg.cylinder_radius = bond_radius * 0.7
        cfg.base_color = (0.8, 0.8, 0.8)
        ch_bond = ShapeFactory.create_shape(ShapeType.CYLINDER, cfg)
        root.add(
            TransformNode(
                f"ch_bond_{i}",
                Translate(mid_x, mid_y, 0.0),
                [
                    TransformNode(
                        f"ch_bond_{i}_rot",
                        Composite(
                            [
                                Rotate(axis=(0, 0, 1), angle=ch_angle),
                                Rotate(axis=(0, 1, 0), angle=90),
                            ]
                        ),
                        [GeometryNode(f"ch_bond_{i}_geo", ch_bond)],
                    )
                ],
            )
        )

    # Add light
    light_cfg = ShapeConfig()
    light = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, light_cfg)
    root.add(
        TransformNode(
            "scene_light",
            Translate(30.0, 30.0, 30.0),
            [LightNode("light", light)],
        )
    )

    return root


register_scene("benzene", build)
