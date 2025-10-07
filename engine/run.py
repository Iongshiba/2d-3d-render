from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from config import EngineConfig, ShapeConfig, CameraConfig, TrackballConfig
from app import App
from config.enums import (
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
        shape=ShapeType.CYLINDER,
        shape_config=ShapeConfig(
            # fmt: off
            cylinder_height=1.0,
            cylinder_radius=0.5,
            cylinder_sectors=3,
            
            sphere_radius=2.0,
            sphere_sectors=100,
            sphere_stacks=101,
            
            ellipse_a=1,
            ellipse_b=0.5,

            torus_horizontal_radius=5,
            torus_vertical_radius=4.9,
            torus_sectors=100,
            torus_stacks=100,

            star_wing=10,
            star_outer_radius=1.5,
            star_inner_radius=1,

            equation_expression="cos(x) + sin(y)",
            equation_mesh_size=100,
            equation_mesh_density=100,

            model_file=r"C:\Users\trand\longg\document\college\hk251\computer_graphic\2d-3d-render\engine\assets\catn0.obj",
            texture_file=r"C:\Users\trand\longg\document\college\hk251\computer_graphic\2d-3d-render\engine\textures\cat_text_m.jpg"
            # texture_file=r"C:\Users\trand\longg\document\college\hk251\computer_graphic\2d-3d-render\engine\textures\wall.jpg"
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
    app.run()


if __name__ == "__main__":
    main()
