from __future__ import annotations

from OpenGL import GL

from config import CameraConfig, EngineConfig
from core.enums import (
    ColorMode,
    RenderMode,
    ShadingModel,
    ShapeType,
    TextureMode,
)
from shape.factory import ShapeFactory
from rendering.strategies import (
    FillRenderingStrategy,
    RenderingStrategy,
    WireframeRenderingStrategy,
)
from rendering.camera import Camera, CameraMovement
from utils import shader_program
from rendering.world import Transform


class Renderer:
    def __init__(self, config):
        self.config = config
        self.camera = Camera(config.camera)
        self.shape = ShapeFactory.create_shape(config.shape, config)
        self.world = Transform()

        # GL state (simple defaults)
        GL.glViewport(0, 0, self.config.width, self.config.height)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
        GL.glClearColor(0.07, 0.07, 0.07, 1.0)

    def render(self, app=None):
        aspect_ratio = (
            float(app.get_aspect_ratio())
            if app and hasattr(app, "get_aspect_ratio")
            else float(self.config.width) / float(self.config.height)
        )
        self.camera.aspect_ratio = aspect_ratio

        projection_matrix = self.camera.get_projection_matrix()
        view_matrix = self.camera.get_view_matrix()
        rotationx_matrix = self.world.get_rotate_matrix("x")
        rotationy_matrix = self.world.get_rotate_matrix("y")
        translate_matrix = self.world.get_translate_matrix(0, 0, 0)
        identity_matrix = self.world.get_identity_matrix()
        print(view_matrix)
        model_matrix = self.world.combine([rotationx_matrix, rotationy_matrix])
        self.shape.transform(
            projection_matrix,
            view_matrix,
            model_matrix,
        )
        self.shape.draw()

    def move_camera(self, movement: CameraMovement, step_scale: float = 1.0) -> None:
        self.camera.process_keyboard(movement, step_scale)
