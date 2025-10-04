import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# fmt: off
class Cube(Shape):
    def __init__(self, vertex_file, fragment_file):
        super().__init__(vertex_file, fragment_file)

        vertices = [
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
        
        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)

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

        vao = VAO()
        vao.add_vbo(
            location=0,
            data=coords,
            ncomponents=coords.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_vbo(
            location=1, 
            data=colors,
            ncomponents=colors.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_ebo(
            indices
        )

        self.shapes.extend(
            [Part(vao, GL.GL_TRIANGLE_STRIP, coords.shape[0], indices.shape[0])]
        )
