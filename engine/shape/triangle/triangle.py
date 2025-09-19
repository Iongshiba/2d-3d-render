import numpy as np

from OpenGL import GL

from libs.vertex import Vertex
from shape.base import Shape


# fmt: off
class Triangle(Shape):
    def __init__(self, vertex_file, fragment_file):
        super().__init__(vertex_file, fragment_file)

        vertex_objects = [
            Vertex(-1, -1, 0.0),
            Vertex(1, -1, 0.0),
            Vertex(0.0, 1, 0.0),
        ]

        coords = np.array([
            o.vertex.flatten() for o in vertex_objects
        ], dtype=np.float32)
        colors = np.array([
            o.color.flatten() for o in vertex_objects
        ], dtype=np.float32)

        self.setup_buffers({0: coords, 1: colors}, indices=None)

    def draw(self):
        self.shader_program.activate()
        self.vao.activate()

        # transformation
        self.transform(self.scale, 0.25)
        self.transform(self.translate)
        self.transform(self.rotate, 'x')

        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)  # Doesn't require EBO

        self.vao.deactivate()
        self.shader_program.deactivate()
