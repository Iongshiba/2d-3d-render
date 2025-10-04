import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Circle(Shape):
    def __init__(self, vertex_file, fragment_file, sector):
        super().__init__(vertex_file, fragment_file)

        angles = np.linspace(0, 2 * np.pi, sector + 1)
        vertices = [Vertex(0.0, 0.0, 0.0)]
        vertices.extend(
            [
                Vertex(
                    np.cos(angle),
                    np.sin(angle),
                    0.0,
                )
                for angle in angles
            ]
        )

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

        self.shapes.extend([Part(vao, GL.GL_TRIANGLE_FAN, len(vertices))])
