from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from app import App
from rendering.renderer import Renderer
from rendering.world import Translate, Rotate, Scale
from config import EngineConfig, CameraConfig, TrackballConfig, ShapeConfig
from config.enums import ShapeType
from graphics.scene import Node, TransformNode, GeometryNode, LightNode
from shape import ShapeFactory


def main():
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

    app = App(cfg.width, cfg.height, use_trackball=True)
    renderer = Renderer(cfg)

    scene = Node("root")

    # Sphere 1
    scene.add(
        TransformNode(
            "translate_1",
            Translate(3, 0, 0),
            [
                GeometryNode(
                    "sphere_1", ShapeFactory.create_shape(ShapeType.SPHERE, shape_cfg)
                )
            ],
        )
    )

    # Sphere 2
    scene.add(
        TransformNode(
            "translate_2",
            Translate(-3, 3, 0),
            [
                GeometryNode(
                    "sphere_2", ShapeFactory.create_shape(ShapeType.SPHERE, shape_cfg)
                )
            ],
        )
    )

    # Light
    scene.add(
        TransformNode(
            "translate_3",
            Translate(0, 3, 5),
            [
                # fmt:off
                LightNode(
                    "light", ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, shape_cfg)
                )
            ],
        )
    )

    renderer.set_scene(scene)
    app.add_renderer(renderer)
    app.run()


if __name__ == "__main__":
    main()
