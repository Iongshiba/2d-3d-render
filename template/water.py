"""Preset scene for a water (H2O) molecule."""

from __future__ import annotations

import math

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


_HALF_BOND_ANGLE = math.radians(104.5 / 2.0)
_H2O_DIRECTIONS = (
    (math.sin(_HALF_BOND_ANGLE), 0.0, math.cos(_HALF_BOND_ANGLE)),
    (-math.sin(_HALF_BOND_ANGLE), 0.0, math.cos(_HALF_BOND_ANGLE)),
)


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=2,
        bond_length=4.5,
        radii=(2.2, 1.0),
        bond_radius=0.18,
        core_color=(0.9, 0.1, 0.1),
        shell_color=(0.95, 0.95, 0.95),
        bond_color=(0.8, 0.8, 0.8),
        directions=_H2O_DIRECTIONS,
        bond_orders=(1, 1),
    )


register_scene("water", build)
