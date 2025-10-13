"""Solar-system inspired demo scene."""

from __future__ import annotations

from config import ShapeConfig, ShapeType
from graphics.scene import GeometryNode, LightNode, Node, TransformNode
from rendering.animation import circular_orbit, infinite_spin, pulse_scale
from rendering.world import Rotate, Scale, Translate
from shape import ShapeFactory


COLORS = {
    "star": (1.0, 0.85, 0.3),
    "planet": (0.25, 0.55, 1.0),
    "moon": (0.9, 0.9, 0.9),
}


def _create_sphere(radius: float, color: tuple[float, float, float]):
    sphere_cfg = ShapeConfig()
    sphere_cfg.sphere_radius = radius
    sphere_cfg.sphere_color = color
    sphere_cfg.sphere_sectors = 40
    sphere_cfg.sphere_stacks = 40
    return ShapeFactory.create_shape(ShapeType.SPHERE, sphere_cfg)


def _build_star() -> TransformNode:
    star = _create_sphere(2.5, COLORS["star"])
    spin = Rotate(axis=(0.0, 1.0, 0.0), angle=0.0, animate=infinite_spin(20.0))
    pulse = Scale(
        1.0, 1.0, 1.0, animate=pulse_scale(minimum=0.9, maximum=1.1, speed=2.0)
    )
    star_node = GeometryNode("star_geom", star)
    return TransformNode(
        "star_root", spin, [TransformNode("star_pulse", pulse, [star_node])]
    )


def _build_planet_system(
    name: str, orbit_radius: float, orbit_speed: float
) -> TransformNode:
    planet_shape = _create_sphere(1.0, COLORS["planet"])
    planet_rotate = Rotate(axis=(0.0, 1.0, 0.0), angle=0.0, animate=infinite_spin(30.0))
    planet_node = GeometryNode(f"{name}_planet", planet_shape)

    moon_shape = _create_sphere(0.3, COLORS["moon"])
    moon_parent = TransformNode(
        f"{name}_moon_orbit",
        Translate(
            0.0,
            0.0,
            2.5,
            animate=circular_orbit(speed=orbit_speed * 2.0, radius=2.5, axis="xz"),
        ),
        [GeometryNode(f"{name}_moon", moon_shape)],
    )

    planet_parent = TransformNode(
        f"{name}_planet_root",
        Rotate(
            axis=(0.0, 1.0, 0.0),
            angle=0.0,
            # animate=circular_orbit(speed=orbit_speed, radius=orbit_radius, axis="xz"),
        ),
        [
            TransformNode(f"{name}_planet_spin", planet_rotate, [planet_node]),
            moon_parent,
        ],
    )

    return planet_parent


def build() -> Node:
    scene = Node("solar_scene")
    scene.add(_build_star())
    scene.add(_build_planet_system("planet_a", 7.5, 0.4))
    scene.add(_build_planet_system("planet_b", 12.0, 0.25))

    light_cfg = ShapeConfig()
    light = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, light_cfg)
    scene.add(
        TransformNode(
            "light",
            Translate(0.0, 10.0, 0.0),
            [LightNode("light_geom", light)],
        )
    )

    return scene


from . import register_scene

register_scene("solar", build)
