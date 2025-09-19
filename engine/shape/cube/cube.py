import numpy as np

from OpenGL import GL

from libs.vertex import Vertex
from shape.base import Shape


# fmt: off
class Cube(Shape):
    def __init__(self, vertex_file, fragment_file):
        super().__init__(vertex_file, fragment_file)

        vertex_objects = [
            # bottom square
            Vertex(-0.5, 0.5, -0.5),
            Vertex(0.5, 0.5, -0.5),
            Vertex(-0.5, -0.5, -0.5),
            Vertex(0.5, -0.5, -0.5),
            # top square
            Vertex(-0.5, 0.5, 0.5),
            Vertex(0.5, 0.5, 0.5),
            Vertex(-0.5, -0.5, 0.5),
            Vertex(0.5, -0.5, 0.5),
        ]
        
        coords = np.array([
            o.vertex.flatten() for o in vertex_objects
        ], dtype=np.float32)
        colors = np.array([
            o.color.flatten() for o in vertex_objects
        ], dtype=np.float32)

        indices = np.array([
            # bottom
            0, 1, 2,
            3, 2, 1,
            # top
            4, 6, 5,
            7, 5, 6,
            # left
            4, 0, 6,
            2, 6, 0,
            # right
            5, 7, 1,
            3, 1, 7,
            # front
            6, 2, 7,
            3, 7, 2,
            # back
            0, 4, 1,
            5, 1, 4,
        ], dtype=np.uint32)

        self.setup_buffers({0: coords, 1: colors}, indices)

    def draw(self, app=None):
        self.shader_program.activate()
        self.vao.activate()

        # Clear window
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Get aspect ratio from app if available
        aspect_ratio = 1.0
        if app and hasattr(app, 'get_aspect_ratio'):
            aspect_ratio = app.get_aspect_ratio()

        # Create transformation matrices
        projection = self.project(fov=70, aspect_ratio=aspect_ratio, near=0.1, far=100.0)
        rotation = self.rotate('x')
        scale = self.scale(1)
        
        # Move cube back so it's visible (at z = -3)
        # view_translation = np.copy(self.transform_matrix)
        # view_translation[2, 3] = -3.0  # Move back along z-axis
        
        # Combine transformations: projection * view * rotation
        # final_transform = np.dot(projection, np.dot(view_translation, rotation))
        
        # self.transform([])

        # Draw the cube
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

        self.vao.deactivate()
        self.shader_program.deactivate()
