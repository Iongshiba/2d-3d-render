"""Preset scene for an oxygen (O2) molecule."""

from __future__ import annotations

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


_O2_DIRECTIONS = (
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
)


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=2,
        bond_length=5.0,
        radii=(1.8, 1.8),  # Both oxygen atoms
        bond_radius=0.25,
        core_color=(0.9, 0.1, 0.1),  # Red for Oxygen
        shell_color=(0.9, 0.1, 0.1),
        bond_color=(0.75, 0.75, 0.75),
        directions=_O2_DIRECTIONS,
        bond_orders=(2, 2),  # Double bond
    )


register_scene("oxygen", build)
