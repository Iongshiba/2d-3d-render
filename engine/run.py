from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from config import EngineConfig, ShapeConfig, CameraConfig
from core.app import App
from core.enums import (
    ColorMode,
    RenderMode,
    ShadingModel,
    ShapeType,
    TextureMode,
)
from rendering.renderer import Renderer


def main():
    cfg = EngineConfig(
        width=1000,
        height=1000,
        shape=ShapeType.CUBE,
        shape_config=ShapeConfig(
            cylinder_height=1.0,
            cylinder_radius=0.5,
            cylinder_sectors=20,
            sphere_radius=2.0,
            sphere_sectors=40,
            sphere_stacks=41,
        ),
        camera=CameraConfig(
            move_speed=1,
            position=(0.0, 0.0, 4.0),
            fov=75,
        ),
    )

    app = App(cfg.width, cfg.height)
    renderer = Renderer(cfg)

    app.add_renderer(renderer)
    # app.add_shape(renderer.shape)
    app.run()


if __name__ == "__main__":
    main()
