"""Preset scene for an ammonia (NH3) molecule."""

from __future__ import annotations

import math

from graphics.scene import Node

from .molecule import generate_molecule
from . import register_scene


# NH3 has a trigonal pyramidal geometry, ~107° bond angles
# Place 3 H atoms at 120° apart, tilted up from the xy-plane
_TILT_ANGLE = math.radians(70)  # Tilt from horizontal
_NH3_DIRECTIONS = (
    (
        math.cos(math.radians(0)) * math.cos(_TILT_ANGLE),
        math.sin(math.radians(0)) * math.cos(_TILT_ANGLE),
        math.sin(_TILT_ANGLE),
    ),
    (
        math.cos(math.radians(120)) * math.cos(_TILT_ANGLE),
        math.sin(math.radians(120)) * math.cos(_TILT_ANGLE),
        math.sin(_TILT_ANGLE),
    ),
    (
        math.cos(math.radians(240)) * math.cos(_TILT_ANGLE),
        math.sin(math.radians(240)) * math.cos(_TILT_ANGLE),
        math.sin(_TILT_ANGLE),
    ),
)


def build() -> Node:
    return generate_molecule(
        centroid=(0.0, 0.0, 0.0),
        attached_count=3,
        bond_length=4.0,
        radii=(1.8, 1.0),  # N and H radii
        bond_radius=0.18,
        core_color=(0.2, 0.2, 0.8),  # Blue for Nitrogen
        shell_color=(0.95, 0.95, 0.95),  # White for Hydrogen
        bond_color=(0.8, 0.8, 0.8),
        directions=_NH3_DIRECTIONS,
        bond_orders=(1, 1, 1),
    )


register_scene("ammonia", build)
