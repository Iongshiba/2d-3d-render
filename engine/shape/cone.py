import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# fmt: on
class Cone(Shape):
    def __init__(self, vertex_file, fragment_file, height, radius, sector):
        super().__init__(vertex_file, fragment_file)

        self.height = height
        self.radius = radius
        self.sector = sector

        vertices = [Vertex(0, 0, height / 2.0), Vertex(0, 0, -height / 2.0)]
        for point in range(1, sector + 1):
            angle = 2.0 * np.pi * point / sector
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append(Vertex(x, y, -height / 2.0))
        vertices.append(vertices[2])

        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)

        top_indices = np.array(
            [0] + list(range(2, len(vertices) + 1)),
            dtype=np.int32,
        )
        bottom_indices = np.array(
            [1] + list(range(2, len(vertices) + 1)),
            dtype=np.int32,
        )

        top_vao = VAO()
        top_vao.add_vbo(
            location=0,
            data=coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        top_vao.add_vbo(
            location=1,
            data=colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        top_vao.add_ebo(
            top_indices,
        )

        bottom_vao = VAO()
        bottom_vao.add_vbo(
            location=0,
            data=coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        bottom_vao.add_vbo(
            location=1,
            data=colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        bottom_vao.add_ebo(
            bottom_indices,
        )

        # fmt: off
        self.shapes.extend(
            [
                Part(top_vao, GL.GL_TRIANGLE_FAN, len(vertices), len(top_indices)),
                Part(bottom_vao, GL.GL_TRIANGLE_FAN, len(vertices), len(bottom_indices)),
            ]
        )
