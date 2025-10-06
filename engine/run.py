from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from config import EngineConfig, ShapeConfig, CameraConfig, TrackballConfig
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
        shape=ShapeType.EQUATION,
        shape_config=ShapeConfig(
            # fmt: off
            cylinder_height=1.0,
            cylinder_radius=0.5,
            cylinder_sectors=5,
            
            sphere_radius=2.0,
            sphere_sectors=100,
            sphere_stacks=101,
            
            ellipse_a=1,
            ellipse_b=0.5,

            star_wing=10,
            star_outer_radius=1.5,
            star_inner_radius=1,

            equation_expression="((x**2 + y**2 - 1)**3 - x**2 * y**3) * -1",
            equation_mesh_size=3,
            equation_mesh_density=100,
        ),
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

    app = App(cfg.width, cfg.height, use_trackball=True)
    renderer = Renderer(cfg)

    app.add_renderer(renderer)
    # app.add_shape(renderer.shape)
    app.run()


if __name__ == "__main__":
    main()
