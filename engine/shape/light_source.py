import numpy as np

from OpenGL import GL

from utils import *
from graphics.buffer import VAO
from graphics.vertex import Vertex
from shape.base import Shape, Part


# fmt: off
class LightSource(Shape):
    def __init__(
        self,
        color=(1.0, 1.0, 1.0),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ) -> None:
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.color = (
            np.array(color, dtype=np.float32)
            if color is not None
            else np.array([1.0, 1.0, 1.0], dtype=np.float32)
        )

        radius = 1.0
        sector = 30
        stack = 30

        sectors = np.linspace(0, 2 * np.pi, sector)
        stacks = np.linspace(-np.pi / 2.0, np.pi / 2.0, stack)

        sides = []
        indices = []

        for stack_idx in range(stack):
            for sector_idx in range(sector):

                sides.extend(
                    [
                        Vertex(
                            radius * np.cos(sectors[sector_idx]) * np.cos(stacks[stack_idx]),
                            radius * np.sin(sectors[sector_idx]) * np.cos(stacks[stack_idx]),
                            radius * np.sin(stacks[stack_idx]),
                            1.0,
                            0.0,
                            1.0
                        ),
                    ]
                )
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
    
    def transform(self, project_matrix, view_matrix, model_matrix):
        homogeneous = np.append(self.position, 1.0)
        transformed = np.dot(model_matrix, homogeneous)
        self.position = transformed[:3]
        
        super().transform(project_matrix, view_matrix, model_matrix)


    def get_color(self):
        return self.color
    
    def get_position(self):
        return self.position
