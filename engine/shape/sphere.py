import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from shape.base import Shape, ShapeCandidate


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
        X, Y = np.meshgrid(sectors, stacks, indexing="xy")
        top = [Vertex(0, 0, radius)]
        bottom = [Vertex(0, 0, -radius)]

        for sector in sectors:
            top.append(
                Vertex(
                    radius * np.cos(sector) * np.cos(stacks[-2]),
                    radius * np.sin(sector) * np.cos(stacks[-2]),
                    radius * np.sin(stacks[-2]),
                )
            )
            bottom.append(
                Vertex(
                    radius * np.cos(sector) * np.cos(stacks[1]),
                    radius * np.sin(sector) * np.cos(stacks[1]),
                    radius * np.sin(stacks[1]),
                )
            )

        sides = []

        for stack_idx in range(len(stacks) - 1):
            stack = stacks[stack_idx]
            side = []
            for sector_idx in range(len(sectors)):
                sector = sectors[sector_idx]
                side += [
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
            sides.append(side)

        top_coords = vertices_to_coords(top)
        top_colors = vertices_to_colors(top)
        bottom_coords = vertices_to_coords(bottom)
        bottom_colors = vertices_to_colors(bottom)

        self.shape_candidates = [
            ShapeCandidate(0, GL.GL_TRIANGLE_FAN, {0: top_coords, 1: top_colors}),
            ShapeCandidate(1, GL.GL_TRIANGLE_FAN, {0: bottom_coords, 1: bottom_colors}),
            *[
                ShapeCandidate(
                    i + 2,
                    GL.GL_TRIANGLE_STRIP,
                    {0: vertices_to_coords(side), 1: vertices_to_colors(side)},
                )
                for i, side in enumerate(sides)
            ],
        ]

        self.setup_buffers()

    def translate(self):
        transform_matrix = np.copy(self.identity)
        # Move the cube back along -Z so it falls within the perspective frustum
        transform_matrix[2, 3] = -5
        return transform_matrix

    def draw(self, app=None):
        def render(candidate, _):
            translate = self.translate()
            rotatex = self.rotate("x")
            rotatey = self.rotate("y")

            self.transform([translate, rotatex, rotatey])

            self._draw_shape(candidate)

        self._draw_candidates(app, render)
