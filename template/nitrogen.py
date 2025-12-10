"""Preset scene for nitrogen (N2) diatomic molecule (approx)."""

from __future__ import annotations

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=1,
        bond_length=4.2,
        radii=(1.0, 0.8),
        bond_radius=0.12,
        core_color=(0.7, 0.7, 0.9),
        shell_color=(0.7, 0.7, 0.9),
        bond_color=(0.6, 0.6, 0.6),
        bond_orders=[3],
    )


register_scene("nitrogen", build)
