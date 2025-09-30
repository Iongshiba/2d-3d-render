import numpy as np

from OpenGL import GL

from graphics.vertex import Vertex
from shape.base import Shape, ShapeCandidate


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

        self.shape_candidates = [
            ShapeCandidate(0, GL.GL_TRIANGLES, {0: coords, 1: colors})
        ]
        self.setup_buffers()
