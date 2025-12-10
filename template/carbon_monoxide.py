"""Preset scene for carbon monoxide (CO) diatomic molecule (approx)."""

from __future__ import annotations

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=1,
        bond_length=4.0,
        radii=(1.0, 0.8),
        bond_radius=0.12,
        core_color=(0.2, 0.2, 0.2),
        shell_color=(0.9, 0.9, 0.9),
        bond_color=(0.6, 0.6, 0.6),
        bond_orders=[3],
    )


register_scene("carbon_monoxide", build)
