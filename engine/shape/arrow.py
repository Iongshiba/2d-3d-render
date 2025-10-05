import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Arrow(Shape):
    def __init__(self, vertex_file, fragment_file):
        super().__init__(vertex_file, fragment_file)

        # fmt: off
        # Arrow head
        triangle_vertices = [
            Vertex(0.5, -1.0, 0.0),
            Vertex(1.0,  0.0, 0.0),
            Vertex(0.5,  1.0, 0.0),
        ]

        triangle_coords = vertices_to_coords(triangle_vertices)
        triangle_colors = vertices_to_colors(triangle_vertices)

        triangle_vao = VAO()
        triangle_vao.add_vbo(
            location=0,
            data=triangle_coords,
            ncomponents=triangle_coords.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        triangle_vao.add_vbo(
            location=1,
            data=triangle_colors,
            ncomponents=triangle_colors.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        # Arrow body
        rectangle_vertices = [
            Vertex( -1.0,  0.5, 0.0),
            Vertex( -1.0, -0.5, 0.0),
            Vertex(  0.5,  0.5, 0.0),
            Vertex(  0.5, -0.5, 0.0),
        ]

        rectangle_coords = vertices_to_coords(rectangle_vertices)
        rectangle_colors = vertices_to_colors(rectangle_vertices)

        rectangle_vao = VAO()
        rectangle_vao.add_vbo(
            location=0,
            data=rectangle_coords,
            ncomponents=rectangle_coords.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        rectangle_vao.add_vbo(
            location=1,
            data=rectangle_colors,
            ncomponents=rectangle_colors.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        self.shapes.extend(
            [
                Part(triangle_vao, GL.GL_TRIANGLE_STRIP, len(triangle_vertices)),
                Part(rectangle_vao, GL.GL_TRIANGLE_STRIP, len(rectangle_vertices)),
            ]
        )
