"""Ball-and-stick style molecule scene builder."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from config import ShapeConfig, ShapeType
from graphics.scene import GeometryNode, LightNode, Node, TransformNode
from rendering.world import Rotate, Translate
from shape.factory import ShapeFactory


DEFAULT_CORE_COLOR = (0.85, 0.2, 0.2)
DEFAULT_SHELL_COLOR = (0.2, 0.55, 0.85)
DEFAULT_BOND_COLOR = (0.8, 0.8, 0.8)


@dataclass(slots=True)
class MoleculeConfig:
    centroid: Sequence[float] = (0.0, 0.0, 0.0)
    attached_count: int = 4
    bond_length: float = 6.0
    radii: Sequence[float] = (2.0, 1.2)
    bond_radius: float = 0.25
    core_color: Sequence[float] = DEFAULT_CORE_COLOR
    shell_color: Sequence[float] = DEFAULT_SHELL_COLOR
    bond_color: Sequence[float] = DEFAULT_BOND_COLOR
    directions: Sequence[Sequence[float]] | None = None
    bond_orders: Sequence[int] | None = None


def _unit_vectors(count: int) -> Iterable[np.ndarray]:
    if count <= 0:
        return ()
    phi = math.pi * (3.0 - math.sqrt(5.0))
    return (
        np.array(
            [
                math.cos(phi * i) * math.sqrt(1.0 - z**2),
                math.sin(phi * i) * math.sqrt(1.0 - z**2),
                z,
            ]
        )
        for i, z in ((i, 1.0 - 2.0 * (i + 0.5) / count) for i in range(count))
    )


def _make_sphere(radius: float, color: Sequence[float]) -> GeometryNode:
    cfg = ShapeConfig()
    cfg.sphere_radius = radius
    cfg.base_color = tuple(color)
    sphere = ShapeFactory.create_shape(ShapeType.SPHERE, cfg)
    return GeometryNode("sphere", sphere)


def _make_bond(length: float, radius: float, color: Sequence[float]) -> GeometryNode:
    cfg = ShapeConfig()
    cfg.cylinder_height = length
    cfg.cylinder_radius = radius
    cfg.base_color = tuple(color)
    bond = ShapeFactory.create_shape(ShapeType.CYLINDER, cfg)
    return GeometryNode("bond", bond)


def _orthonormal_basis(direction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    axis = direction / np.linalg.norm(direction)
    helper = np.array([0.0, 1.0, 0.0])
    if abs(float(np.dot(axis, helper))) > 0.99:
        helper = np.array([1.0, 0.0, 0.0])
    perpendicular = np.cross(axis, helper)
    perpendicular /= np.linalg.norm(perpendicular)
    second = np.cross(axis, perpendicular)
    return perpendicular, second


def _bond_offsets(
    direction: np.ndarray, order: int, base_radius: float
) -> list[np.ndarray]:
    if order <= 1:
        return [np.zeros(3, dtype=float)]
    first, second = _orthonormal_basis(direction)
    spacing = base_radius * 1.5
    offsets: list[np.ndarray] = []
    for idx in range(order):
        angle = (2.0 * math.pi * idx) / order
        offset = (math.cos(angle) * first + math.sin(angle) * second) * spacing
        offsets.append(offset)
    return offsets


def _bond_radius_for_order(base_radius: float, order: int) -> float:
    if order <= 1:
        return base_radius
    if order == 2:
        return base_radius * 0.75
    return base_radius * 0.6


def _rotation_from_z(direction: np.ndarray) -> Rotate | None:
    base = np.array([0.0, 0.0, 1.0])
    norm = np.linalg.norm(direction)
    if norm == 0.0:
        return None
    direction = direction / norm
    dot = float(np.clip(np.dot(base, direction), -1.0, 1.0))
    angle = math.degrees(math.acos(dot))
    if angle == 0.0:
        return None
    axis = np.cross(base, direction)
    axis_norm = np.linalg.norm(axis)
    if axis_norm == 0.0:
        axis = np.array([1.0, 0.0, 0.0])
    else:
        axis = axis / axis_norm
    return Rotate(axis=tuple(axis.tolist()), angle=angle)


def build_ball_and_stick(config: MoleculeConfig | None = None) -> Node:
    cfg = config if config is not None else MoleculeConfig()
    centroid = np.array(cfg.centroid, dtype=float)
    if len(cfg.radii) == 0:
        raise ValueError("MoleculeConfig.radii must contain at least one radius value.")
    core_radius = float(cfg.radii[0])
    shell_radius = float(cfg.radii[1]) if len(cfg.radii) > 1 else core_radius
    root = Node("molecule_root")

    core = _make_sphere(core_radius, cfg.core_color)
    root.add(
        TransformNode(
            "core_translate",
            Translate(*centroid),
            [core],
        )
    )

    if cfg.directions is not None:
        raw_directions = [np.asarray(vec, dtype=float) for vec in cfg.directions]
    else:
        raw_directions = list(_unit_vectors(cfg.attached_count))

    if cfg.bond_orders is not None:
        if len(cfg.bond_orders) != len(raw_directions):
            raise ValueError("MoleculeConfig.bond_orders must match number of bonds.")
        orders = [int(max(1, min(3, order))) for order in cfg.bond_orders]
    else:
        orders = [1] * len(raw_directions)

    for index, direction in enumerate(raw_directions):
        norm = np.linalg.norm(direction)
        if norm == 0.0:
            continue
        direction = direction / norm
        atom_center = centroid + direction * cfg.bond_length
        bond_midpoint = centroid + direction * (cfg.bond_length * 0.5)

        bond_rotation = _rotation_from_z(direction)
        order = orders[index]
        bond_radius = _bond_radius_for_order(cfg.bond_radius, order)
        offsets = _bond_offsets(direction, order, cfg.bond_radius)

        for bond_idx, offset in enumerate(offsets):
            bond_geometry = _make_bond(cfg.bond_length, bond_radius, cfg.bond_color)
            bond_children: list[TransformNode | GeometryNode] = [bond_geometry]
            if bond_rotation is not None:
                bond_children = [
                    TransformNode(
                        f"bond_{index}_{bond_idx}_rotate",
                        bond_rotation,
                        [bond_geometry],
                    )
                ]

            root.add(
                TransformNode(
                    f"bond_{index}_{bond_idx}",
                    Translate(*(bond_midpoint + offset)),
                    bond_children,
                )
            )

        shell = _make_sphere(shell_radius, cfg.shell_color)
        root.add(
            TransformNode(
                f"shell_{index}",
                Translate(*atom_center),
                [shell],
            )
        )

    light_cfg = ShapeConfig()
    light = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, light_cfg)
    root.add(
        TransformNode(
            "scene_light",
            Translate(30.0, 30.0, 30.0),
            [LightNode("light", light)],
        )
    )

    return root


def generate_molecule(
    centroid: Sequence[float] = (0.0, 0.0, 0.0),
    attached_count: int = 4,
    bond_length: float = 6.0,
    radii: Sequence[float] = (2.0, 1.2),
    bond_radius: float = 0.25,
    core_color: Sequence[float] = DEFAULT_CORE_COLOR,
    shell_color: Sequence[float] = DEFAULT_SHELL_COLOR,
    bond_color: Sequence[float] = DEFAULT_BOND_COLOR,
    directions: Sequence[Sequence[float]] | None = None,
    bond_orders: Sequence[int] | None = None,
) -> Node:
    config = MoleculeConfig(
        centroid=centroid,
        attached_count=attached_count,
        bond_length=bond_length,
        radii=radii,
        bond_radius=bond_radius,
        core_color=core_color,
        shell_color=shell_color,
        bond_color=bond_color,
        directions=directions,
        bond_orders=bond_orders,
    )
    return build_ball_and_stick(config)


def build() -> Node:
    return generate_molecule()


from . import register_scene

register_scene("molecule", build)
