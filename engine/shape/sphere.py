import numpy as np

from OpenGL import GL

from utils import *
from graphics.buffer import VAO
from graphics.vertex import Vertex
from shape.base import Shape, Part


# fmt: on
class Sphere(Shape):
    def __init__(self, vertex_file, fragment_file, texture_file, radius, sector, stack):
        if stack % 2 != 1:
            raise ValueError("stack value must be odd")
        super().__init__(vertex_file, fragment_file)
        self._create_texture(texture_file)

        self.radius = radius
        self.sector = sector
        self.stack = stack

        sectors = np.linspace(0, 2 * np.pi, sector + 1)
        stacks = np.linspace(-np.pi / 2.0, np.pi / 2.0, stack)

        sides = []
        texcoords = []

        stack_count = len(stacks) - 1

        for stack_idx in range(len(stacks) - 1):
            for sector_idx in range(len(sectors)):
                sector = sectors[sector_idx]

                u = sector_idx / sector
                v_top = 1.0 - (stack_idx + 1) / stack_count
                v_bottom = 1.0 - stack_idx / stack_count

                sides.extend(
                    [
                        Vertex(
                            radius * np.cos(sector) * np.cos(stacks[stack_idx + 1]),
                            radius * np.sin(sector) * np.cos(stacks[stack_idx + 1]),
                            radius * np.sin(stacks[stack_idx + 1]),
                        ),
                        Vertex(
                            radius * np.cos(sector) * np.cos(stacks[stack_idx]),
                            radius * np.sin(sector) * np.cos(stacks[stack_idx]),
                            radius * np.sin(stacks[stack_idx]),
                        ),
                    ]
                )
                texcoords.extend(
                    [
                        (u, v_top),
                        (u, v_bottom),
                    ]
                )

        side_coords = vertices_to_coords(sides)
        side_colors = vertices_to_colors(sides)
        side_texcoords = np.array(texcoords, dtype=np.float32)

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
        side_vao.add_vbo(
            location=2,
            data=side_texcoords,
            ncomponents=2,
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
