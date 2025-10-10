from __future__ import annotations

from OpenGL import GL

from shape.factory import ShapeFactory
from rendering.camera import Camera, CameraMovement, Trackball
from rendering.world import Transform


class Renderer:
    def __init__(self, config):
        self.config = config
        self.camera = Camera(config.camera)
        self.trackball = Trackball(config.trackball)
        self.shape = ShapeFactory.create_shape(config.shape, config)
        self.world = Transform()
        self.app = None

        # GL state (simple defaults)
        GL.glViewport(0, 0, self.config.width, self.config.height)
        GL.glEnable(GL.GL_DEPTH_TEST)
        if config.cull_face:
            GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_FRONT)
        GL.glFrontFace(GL.GL_CCW)
        GL.glClearColor(0.07, 0.07, 0.07, 1.0)

        self.use_trackball = False

    def render(self):
        if not self.app:
            raise ValueError("Must attach to an Application")

        aspect_ratio = (
            float(self.app.get_aspect_ratio())
            if self.app and hasattr(self.app, "get_aspect_ratio")
            else float(self.config.width) / float(self.config.height)
        )
        self.camera.aspect_ratio = aspect_ratio

        projection_matrix = (
            self.camera.get_projection_matrix()
            if not self.use_trackball
            else self.trackball.get_projection_matrix(self.app.winsize)
        )
        view_matrix = (
            self.camera.get_view_matrix()
            if not self.use_trackball
            else self.trackball.get_view_matrix()
        )
        # rotationx_matrix = self.world.get_rotate_matrix("x")
        # rotationy_matrix = self.world.get_rotate_matrix("y")
        # translate_matrix = self.world.get_translate_matrix(0, 0, 0)
        # identity_matrix = self.world.get_identity_matrix()
        # model_matrix = self.world.combine([rotationx_matrix, rotationy_matrix])
        model_matrix = self.world.get_identity_matrix()
        self.shape.transform(
            projection_matrix,
            view_matrix,
            model_matrix,
        )
        self.shape.draw()

    def move_world(self, step_scale: float = 1.0) -> None:
        self.world.process_time(step_scale)

    def move_camera(self, movement: CameraMovement, step_scale: float = 1.0) -> None:
        self.camera.move(movement, step_scale)

    def rotate_camera(self, old, new):
        self.camera.look(old, new)

    def move_trackball(self, old, new):
        self.trackball.pan(old, new)

    def rotate_trackball(self, old, new, winsize):
        self.trackball.drag(old, new, winsize)

    def zoom_trackball(self, delta, winsize):
        self.trackball.zoom(delta, winsize)
