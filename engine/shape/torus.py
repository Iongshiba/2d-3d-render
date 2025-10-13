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
        sector,
        stack,
        horizontal_radius,
        vertical_radius,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ):
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.sector = sector
        self.stack = stack
        self.horizontal_radius = horizontal_radius
        self.vertical_radius = vertical_radius

        sectors = np.linspace(0, 2 * np.pi, sector)
        stacks = np.linspace(0, 2 * np.pi, stack)

        sides = []
        indices = []
        norms = []

        for stack_idx in range(stack):
            for sector_idx in range(sector):
                # fmt: off
                sides.append(
                    Vertex(
                        (horizontal_radius + vertical_radius * np.cos(stacks[stack_idx])) * np.cos(sectors[sector_idx]),
                        (horizontal_radius + vertical_radius * np.cos(stacks[stack_idx])) * np.sin(sectors[sector_idx]),
                        vertical_radius * np.sin(stacks[stack_idx]),
                    ),
                )
                # fmt: on
                vertical_ring_center = np.array(
                    [
                        horizontal_radius * np.cos(sectors[sector_idx]),
                        horizontal_radius * np.sin(sectors[sector_idx]),
                        0,
                    ],
                    dtype=np.float32,
                )
                norms.append(sides[-1].vertex - vertical_ring_center)
                if stack_idx < stack - 1:
                    indices.extend(
                        [
                            stack_idx * sector + sector_idx,
                            (stack_idx + 1) * sector + sector_idx,
                        ]
                    )

        side_coords = vertices_to_coords(sides)
        side_colors = vertices_to_colors(sides)
        indices = np.array(indices, dtype=np.int32)
        norms = np.array(norms, dtype=np.float32)

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
            data=norms,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        side_vao.add_ebo(
            indices,
        )

        self.shapes.extend(
            [
                Part(
                    side_vao,
                    GL.GL_TRIANGLE_STRIP,
                    side_coords.shape[0],
                    indices.shape[0],
                ),
            ]
        )
