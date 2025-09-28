import numpy as np

from OpenGL import GL

from graphics.vertex import Vertex
from shape.base import Shape, ShapeCandidate


# fmt: off
class Cube(Shape):
    def __init__(self, vertex_file, fragment_file):
        super().__init__(vertex_file, fragment_file)

        vertex_objects = [
            # back square with normal outside
            Vertex(-0.5, 0.5, -0.5),
            Vertex(0.5, 0.5, -0.5),
            Vertex(-0.5, -0.5, -0.5),
            Vertex(0.5, -0.5, -0.5),
            # front square
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
            # back with normal go out
            0, 1, 2,
            3, 2, 1,
            # front with normal go out
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

        self.shape_candidates = [
            ShapeCandidate(0, GL.GL_TRIANGLES, {0: coords, 1: colors}, indices)
        ]

        self.setup_buffers()

    def translate(self):
        transform_matrix = np.copy(self.identity)
        # Move the cube back along -Z so it falls within the perspective frustum
        transform_matrix[2, 3] = -2
        return transform_matrix

    def draw(self, app=None):
        def render(candidate, _):
            translate = self.translate()
            rotatey = self.rotate('y')
            rotatex = self.rotate('x')

            self.transform([translate, rotatex, rotatey])
            self._draw_shape(candidate)

        self._draw_candidates(app, render)
