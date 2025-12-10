"""Subwindow configuration for multi-panel UI."""

from enum import Enum, auto


class SubwindowType(Enum):
    """Types of application subwindows."""

    GEOMETRY = auto()  # Geometry shapes and 3D/2D visualization
    GRADIENT_DESCENT = auto()  # Gradient descent visualizer
    CHEMISTRY = auto()  # Chemistry molecules and Bohr model


class ChemistryMode(Enum):
    """Chemistry subwindow display modes."""

    PERIODIC_TABLE = auto()  # Periodic table with Bohr model
    MOLECULES = auto()  # Molecule 3D viewer
    BOHR_MODEL = auto()  # Interactive Bohr model


__all__ = ["SubwindowType", "ChemistryMode"]
