import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# fmt: on
class Cylinder(Shape):
    def __init__(self, vertex_file, fragment_file, height, radius, sector):
        super().__init__(vertex_file, fragment_file)

        self.height = height
        self.radius = radius
        self.sector = sector

        top_circle = [Vertex(0, 0, height / 2.0)]
        bottom_circle = [Vertex(0, 0, -height / 2.0)]
        for point in range(1, sector + 1):
            angle = 2.0 * np.pi * point / sector
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            top_circle.append(Vertex(x, y, height / 2.0))
            bottom_circle.append(Vertex(x, y, -height / 2.0))
        top_circle.append(top_circle[1])
        bottom_circle.append(bottom_circle[1])

        top_coords = vertices_to_coords(top_circle)
        top_colors = vertices_to_colors(top_circle)
        bottom_coords = vertices_to_coords(bottom_circle)
        bottom_colors = vertices_to_colors(bottom_circle)

        side_coords = np.empty(
            (top_coords.shape[0] + bottom_coords.shape[0] - 2, top_coords.shape[1]),
            dtype=np.float32,
        )
        side_coords[0::2] = top_coords[1:]
        side_coords[1::2] = bottom_coords[1:]
        side_colors = np.empty(
            (top_colors.shape[0] + bottom_colors.shape[0] - 2, top_colors.shape[1]),
            dtype=np.float32,
        )
        side_colors[0::2] = top_colors[1:]
        side_colors[1::2] = bottom_colors[1:]

        bottom_coords *= -1

        top_vao = VAO()
        top_vao.add_vbo(
            location=0,
            data=top_coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        top_vao.add_vbo(
            location=1,
            data=top_colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        bottom_vao = VAO()
        bottom_vao.add_vbo(
            location=0,
            data=bottom_coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        bottom_vao.add_vbo(
            location=1,
            data=bottom_colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        side_vao = VAO()
        side_vao.add_vbo(
            location=0,
            data=side_coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        side_vao.add_vbo(
            location=1,
            data=side_colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        
        self.shapes.extend(
            [
                Part(top_vao, GL.GL_TRIANGLE_FAN, top_coords.shape[0]),
                Part(bottom_vao, GL.GL_TRIANGLE_FAN, bottom_coords.shape[0]),
                Part(side_vao, GL.GL_TRIANGLE_STRIP, side_coords.shape[0]),
            ]
        )
