import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

from config import CameraConfig, EngineConfig, TrackballConfig

from app import App, SceneControlOverlay
from rendering.renderer import Renderer


def build_engine_config() -> EngineConfig:
    return EngineConfig(
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


def main() -> None:
    cfg = build_engine_config()

    app = App(cfg.width, cfg.height, use_trackball=True)
    renderer = Renderer(cfg)
    overlay = SceneControlOverlay(app, renderer)

    app.add_renderer(renderer)
    app.add_ui(overlay)
    app.run()


if __name__ == "__main__":
    main()
