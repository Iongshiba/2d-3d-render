import numpy as np

from OpenGL import GL

from utils import *
from graphics.buffer import VAO
from graphics.vertex import Vertex
from shape.base import Shape, Part


# fmt: on
class Torus(Shape):
    def __init__(
        self,
        vertex_file,
        fragment_file,
        sector,
        stack,
        horizontal_radius,
        vertical_radius,
    ):
        super().__init__(vertex_file, fragment_file)

        self.sector = sector
        self.stack = stack
        self.horizontal_radius = horizontal_radius
        self.vertical_radius = vertical_radius

        sectors = np.linspace(0, 2 * np.pi, sector)
        stacks = np.linspace(0, 2 * np.pi, stack)

        sides = []

        # fmt: off
        for stack_idx in range(stack - 1):
            for sector in sectors:
                sides.extend(
                    [
                        Vertex(
                            (horizontal_radius + vertical_radius * np.cos(stacks[stack_idx])) * np.cos(sector),
                            (horizontal_radius + vertical_radius * np.cos(stacks[stack_idx])) * np.sin(sector),
                            vertical_radius * np.sin(stacks[stack_idx]),
                        ),
                        Vertex(
                            (horizontal_radius + vertical_radius * np.cos(stacks[stack_idx + 1])) * np.cos(sector),
                            (horizontal_radius + vertical_radius * np.cos(stacks[stack_idx + 1])) * np.sin(sector),
                            vertical_radius * np.sin(stacks[stack_idx + 1]),
                        )
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
                Part(side_vao, GL.GL_TRIANGLE_STRIP, side_coords.shape[0]),
            ]
        )
