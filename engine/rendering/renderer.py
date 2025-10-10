from __future__ import annotations

from OpenGL import GL

from shape.base import Shape
from graphics.scene import Node, LightNode, GeometryNode, TransformNode
from rendering.camera import Camera, CameraMovement, Trackball
from rendering.world import Transform


class Renderer:
    def __init__(self, config):
        self.config = config
        self.camera = Camera(config.camera)
        self.trackball = Trackball(config.trackball)

        self.app = None
        self.root = None

        # GL state (simple defaults)
        GL.glViewport(0, 0, self.config.width, self.config.height)
        GL.glEnable(GL.GL_DEPTH_TEST)
        if config.cull_face:
            GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_FRONT)
        GL.glFrontFace(GL.GL_CCW)
        GL.glClearColor(0.07, 0.07, 0.07, 1.0)

        self.use_trackball = False

        self.meshes = []
        self.lights = []

    def set_scene(self, scene):
        self.root = scene

    def _collect_lighting(self, node):
        if isinstance(node, LightNode):
            self.lights.append(node)
        elif isinstance(node, GeometryNode):
            self.meshes.append(node)
        for child in node.children:
            self._collect_lighting(child)

    def _apply_lighting(self):
        for mesh in self.meshes:
            mesh.shape.lighting(self.lights[0].shape.get_color())

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

        self._collect_lighting(self.root)
        self._apply_lighting()
        self.root.draw(None, view_matrix, projection_matrix)

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
