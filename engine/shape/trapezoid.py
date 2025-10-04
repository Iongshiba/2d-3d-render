import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Trapezoid(Shape):
    def __init__(self, vertex_file, fragment_file):
        super().__init__(vertex_file, fragment_file)

        # fmt: off
        vertices = [
            Vertex(-1.0, -0.5, 0.0),
            Vertex(-0.5,  0.5, 0.0),
            Vertex( 1.0, -0.5, 0.0),
            Vertex( 0.5,  0.5, 0.0),
        ]

        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)

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

        self.shapes.extend(
            [Part(vao, GL.GL_TRIANGLE_STRIP, len(vertices))]
        )
