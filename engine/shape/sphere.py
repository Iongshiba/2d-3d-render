import numpy as np

from OpenGL import GL

from utils import *
from graphics.buffer import VAO
from graphics.vertex import Vertex
from shape.base import Shape, Part


# fmt: on
class Sphere(Shape):
    def __init__(self, vertex_file, fragment_file, radius, sector, stack):
        if stack % 2 != 1:
            raise ValueError("stack value must be odd")

        super().__init__(vertex_file, fragment_file)

        self.radius = radius
        self.sector = sector
        self.stack = stack

        sectors = np.linspace(0, 2 * np.pi, sector + 1)
        stacks = np.linspace(-np.pi / 2.0, np.pi / 2.0, stack)

        sides = []

        for stack_idx in range(len(stacks) - 1):
            stack = stacks[stack_idx]
            for sector_idx in range(len(sectors)):
                sector = sectors[sector_idx]
                sides.extend(
                    [
                        Vertex(
                            radius * np.cos(sector) * np.cos(stacks[stack_idx]),
                            radius * np.sin(sector) * np.cos(stacks[stack_idx]),
                            radius * np.sin(stacks[stack_idx]),
                        ),
                        Vertex(
                            radius * np.cos(sector) * np.cos(stacks[stack_idx + 1]),
                            radius * np.sin(sector) * np.cos(stacks[stack_idx + 1]),
                            radius * np.sin(stacks[stack_idx + 1]),
                        ),
                    ]
                )

        side_coords = vertices_to_coords(sides)
        side_colors = vertices_to_colors(sides)

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
                # Part(top_vao, GL.GL_TRIANGLE_FAN, top_coords.shape[0]),
                # Part(bottom_vao, GL.GL_TRIANGLE_FAN, bottom_coords.shape[0]),
                Part(side_vao, GL.GL_TRIANGLE_STRIP, side_coords.shape[0]),
            ]
        )
