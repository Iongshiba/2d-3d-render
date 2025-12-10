"""Preset scene for hydrogen (H2) diatomic molecule."""

from __future__ import annotations

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


def build() -> Node:
    # Single hydrogen atom with one attached (diatomic)
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=1,
        bond_length=4.0,
        radii=(0.8, 0.6),
        bond_radius=0.08,
        core_color=(0.9, 0.9, 0.9),
        shell_color=(0.9, 0.9, 0.9),
        bond_color=(0.8, 0.8, 0.8),
    )


register_scene("hydrogen", build)
