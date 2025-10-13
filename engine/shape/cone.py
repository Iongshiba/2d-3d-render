import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# fmt: on
class Cone(Shape):
    def __init__(
        self,
        height: float,
        radius: float,
        sector: int,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ) -> None:
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.height = height
        self.radius = radius
        self.sector = sector

        vertices = [Vertex(0, 0, height / 2.0), Vertex(0, 0, -height / 2.0)]
        vector_up = vertices[0].vertex - vertices[1].vertex
        top_norms = [vector_up, -vector_up]
        bottom_norms = [vector_up, -vector_up]
        for point in range(1, sector + 1):
            angle = 2.0 * np.pi * point / sector
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append(Vertex(x, y, -height / 2.0))

            # Calculate Norm
            # vector_out = vertices[-1].vertex - vertices[1].vertex
            # vector_diag = vertices[0].vertex - vertices[-1].vertex
            # top_norms.append(np.cross(np.cross(vector_out, vector_up), vector_diag))
            n = np.array([x, y, radius / height])  # need to understand this
            n /= np.linalg.norm(n)
            top_norms.append(n)
            bottom_norms.append(-vector_up)
            bottom_norms.append(-vector_up)

        vertices.append(vertices[2])
        top_norms.append(top_norms[2])
        bottom_norms.append(bottom_norms[2])

        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)
        top_norms = np.array(top_norms, dtype=np.float32)
        bottom_norms = np.array(bottom_norms, dtype=np.float32)

        top_indices = np.array(
            [0] + list(range(2, len(vertices)))[::-1],
            dtype=np.int32,
        )
        bottom_indices = np.array(
            [1] + list(range(2, len(vertices))),
            dtype=np.int32,
        )
        # print(len(top_indices), len(bottom_indices), len(top_norms), len(bottom_norms))

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
        top_vao.add_vbo(
            location=2,
            data=top_norms,
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
        bottom_vao.add_vbo(
            location=2,
            data=bottom_norms,
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
