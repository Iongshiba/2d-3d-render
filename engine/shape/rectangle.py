import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Rectangle(Shape):
    def __init__(
        self,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ) -> None:
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        # fmt: off
        vertices = [
            Vertex(-1.0, -0.5, 0.0, 1.0, 1.0, 1.0),  # Bright white color
            Vertex(-1.0,  0.5, 0.0, 1.0, 1.0, 1.0),  # Bright white color
            Vertex( 1.0, -0.5, 0.0, 1.0, 1.0, 1.0),  # Bright white color
            Vertex( 1.0,  0.5, 0.0, 1.0, 1.0, 1.0),  # Bright white color
        ]
        texcoords = np.array(
            [
                [1.0, 0.0],
                [0.0, 0.0],
                [1.0, 1.0],
                [0.0, 1.0],
            ],
            dtype=np.float32,
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
        if texture_file:
            vao.add_vbo(
                location=3,
                data=texcoords,
                ncomponents=texcoords.shape[1],
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

        self.shapes.extend(
            [Part(vao, GL.GL_TRIANGLE_STRIP, len(vertices))]
        )
