from __future__ import annotations

import os
import sys
import numpy as np

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from app import App
from rendering.renderer import Renderer
from rendering.world import Translate, Rotate, Scale
from config import EngineConfig, CameraConfig, TrackballConfig, ShapeConfig
from config import ShapeType
from graphics.scene import Node, TransformNode, GeometryNode, LightNode
from shape import ShapeFactory, Sphere, Ring, LightSource


cfg = EngineConfig(
    width=1000,
    height=1000,
    camera=CameraConfig(
        move_speed=1,
        position=(0.0, 0.0, 4.0),
        fov=75,
    ),
    trackball=TrackballConfig(
        distance=10.0,
        pan_sensitivity=0.0005,
    ),
)
shape_cfg = ShapeConfig()


# Animation
def infinite_rotate(speed: float = 1.0):
    def update_fn(t: "Rotate", dt: float):
        t.angle = (t.angle + dt * speed) % 360

    return update_fn


def infinite_orbit(speed: float = 1.0, radius: float = 1.0):
    theta = 0

    def update_fn(t: "Translate", dt: float):
        nonlocal theta
        theta = (theta + dt * speed) % (2 * np.pi)
        t.x = np.cos(theta) * radius
        t.y = np.sin(theta) * radius

    return update_fn


def generate_nucleus(x, y, z, radius, sector, stack):
    stacks = np.linspace(-np.pi / 2, np.pi / 2, stack)
    sectors = np.linspace(0, 2 * np.pi, sector)
    proton_color = (0.8, 0.2, 0.2)
    neutron_color = (0.0, 0.8, 0.0)
    color = neutron_color

    atom_sphere = []
    for stack in stacks:
        for sector in sectors:
            color = proton_color if color == neutron_color else neutron_color
            atom_sphere.append(
                TransformNode(
                    "atom_sphere",
                    Translate(
                        radius * np.cos(stack) * np.cos(sector),
                        radius * np.cos(stack) * np.sin(sector),
                        radius * np.sin(stack),
                    ),
                    [GeometryNode("atom", Sphere(1, 20, 20, color))],
                )
            )

    return TransformNode("nucleus", Translate(x, y, z), atom_sphere)


def generate_electron(x, y, z, radius, speed):
    color = (0.2, 0.2, 0.8)
    return TransformNode(
        "electron",
        Translate(
            x,
            y,
            z,
            infinite_orbit(speed, radius),
        ),
        [GeometryNode("atom", Sphere(0.8, 20, 20, color))],
    )


def generate_orbit_ring(x, y, z, radius, sector):
    color = (0.8, 0.8, 0.8)
    return TransformNode(
        "ring",
        Translate(x, y, z),
        [GeometryNode("ring", Ring(radius, sector, color))],
    )


def main():
    app = App(cfg.width, cfg.height, use_trackball=True)
    renderer = Renderer(cfg)

    scene = Node("root")

    scene.add(generate_nucleus(0, 0, 0, 1, 6, 3))

    scene.add(generate_orbit_ring(0, 0, 0, 5, 50))
    scene.add(generate_electron(0, 0, 0, 5, 1))

    scene.add(generate_orbit_ring(0, 0, 0, 10, 50))
    scene.add(generate_electron(0, 0, 0, 10, 1.2))

    scene.add(generate_orbit_ring(0, 0, 0, 15, 50))
    scene.add(generate_electron(0, 0, 0, 15, 1.4))

    scene.add(
        TransformNode(
            "translate",
            Translate(15, 15, 15),
            [
                # TransformNode(
                #     "scale",
                # Scale(2, 2, 2),
                # [
                LightNode(
                    "light",
                    ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, shape_cfg),
                )
                # ],
                # )
            ],
        )
    )

    renderer.set_scene(scene)
    app.add_renderer(renderer)
    app.run()


if __name__ == "__main__":
    main()
