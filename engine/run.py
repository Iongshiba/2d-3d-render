import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from app import App

try:
    from .config import (
        EngineConfig,
        ShapeType,
        ColorMode,
        ShadingModel,
        TextureMode,
        RenderMode,
    )
    from .renderer import Renderer
except Exception:
    from config import (
        EngineConfig,
        ShapeType,
        ColorMode,
        ShadingModel,
        TextureMode,
        RenderMode,
    )
    from renderer import Renderer


def main():
    cfg = EngineConfig(
        width=1000,
        height=1000,
        shape=ShapeType.SPHERE,  # change to TRIANGLE/CUBE/CYLINDER/SPHERE
        color_mode=ColorMode.VERTEX,  # change to FLAT for uniform color
        shading=ShadingModel.NONE,  # placeholder for PHONG
        texture=TextureMode.NONE,  # placeholder
        render_mode=RenderMode.FILL,  # placeholder for wireframe
        flat_color=(0.2, 0.8, 0.3),
        cylinder_height=1.0,
        cylinder_radius=0.5,
        cylinder_sectors=20,
        sphere_radius=2.0,
        sphere_sectors=160,
        sphere_stacks=161,
    )

    app = App(cfg.width, cfg.height)
    renderer = Renderer(cfg)

    app.add_shape(renderer.shape)
    app.run()


if __name__ == "__main__":
    main()
