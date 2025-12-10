"""Preset scene for nitric oxide (NO) diatomic molecule (approx)."""

from __future__ import annotations

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=1,
        bond_length=4.1,
        radii=(1.2, 0.9),
        bond_radius=0.11,
        core_color=(0.8, 0.5, 0.2),
        shell_color=(0.9, 0.4, 0.2),
        bond_color=(0.7, 0.6, 0.6),
        bond_orders=[2],
    )


register_scene("nitric_oxide", build)
