import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Equation(Shape):
    def __init__(
        self,
        expression,
        mesh_size,
        mesh_density,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ):
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.expression = expression
        self.mesh_size = mesh_size
        self.mesh_density = mesh_density

        func = make_numpy_func(expression)
        x_ = np.linspace(-mesh_size / 2, mesh_size / 2, mesh_density)
        y_ = np.linspace(-mesh_size / 2, mesh_size / 2, mesh_density)
        X, Y = np.meshgrid(x_, y_, indexing="xy")
        Z = func(X, Y)
        Z = Z / np.average(Z)

        vertices = [
            Vertex(x, y, z) for x, y, z in zip(X.flatten(), Y.flatten(), Z.flatten())
        ]

        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)

        indices = []
        for i in range(mesh_density - 1):
            strips = []
            for j in range(mesh_density):
                strips.extend(
                    [
                        i * mesh_density + j,
                        (i + 1) * mesh_density + j,
                    ]
                )
            # Remove redundant connection between odd-even strip
            # Only even-odd strip is allowed
            if i < mesh_density - 2:
                last = (i + 1) * mesh_density + (mesh_density - 1)
                next_first = (i + 1) * mesh_density
                strips.extend(
                    [
                        last,
                        last,
                        next_first,
                        next_first,
                    ]
                )
            indices.extend(strips)

        indices = np.array(indices, dtype=np.int32)

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
        vao.add_ebo(indices)

        self.shapes.extend(
            [Part(vao, GL.GL_TRIANGLE_STRIP, len(vertices), len(indices))]
        )
