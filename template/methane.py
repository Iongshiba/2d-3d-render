"""Preset scene for a methane (CH4) molecule."""

from __future__ import annotations

import math

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


# CH4 has tetrahedral geometry, 109.5° bond angles
_TETRAHEDRAL_ANGLE = math.radians(109.5)
_CH4_DIRECTIONS = (
    (1.0, 1.0, 1.0),
    (1.0, -1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (-1.0, -1.0, 1.0),
)

# Normalize directions
import numpy as np

_CH4_DIRECTIONS = tuple(tuple(np.array(d) / np.linalg.norm(d)) for d in _CH4_DIRECTIONS)


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=4,
        bond_length=4.5,
        radii=(2.0, 1.0),  # C and H radii
        bond_radius=0.18,
        core_color=(0.2, 0.2, 0.2),  # Dark gray for Carbon
        shell_color=(0.95, 0.95, 0.95),  # White for Hydrogen
        bond_color=(0.8, 0.8, 0.8),
        directions=_CH4_DIRECTIONS,
        bond_orders=(1, 1, 1, 1),
    )


register_scene("methane", build)
