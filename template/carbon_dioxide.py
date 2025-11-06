"""Preset scene for a carbon dioxide (CO2) molecule."""

from __future__ import annotations

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


_CO2_DIRECTIONS = (
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
)


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=2,
        bond_length=5.5,
        radii=(2.0, 1.6),
        bond_radius=0.22,
        core_color=(0.2, 0.2, 0.2),
        shell_color=(0.85, 0.1, 0.1),
        bond_color=(0.75, 0.75, 0.75),
        directions=_CO2_DIRECTIONS,
        bond_orders=(2, 2),
    )


register_scene("carbon_dioxide", build)
