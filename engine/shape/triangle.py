import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# TODO: CUSTOMIZABLE
class Triangle(Shape):
    def __init__(self, vertex_file, fragment_file, texture_file=None):
        super().__init__(vertex_file, fragment_file)

        # fmt: off
        vertices = [
            Vertex(-1.0, -1.0, 0.0),
            Vertex( 1.0, -1.0, 0.0),
            Vertex( 0.0,  1.0, 0.0),
        ]

        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)

        vao = VAO()
        vao.add_vbo(
            location=0,
            data=coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_vbo(
            location=1,
            data=colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        
        if texture_file:
            self._create_texture(texture_file)
            # Texture coordinate
            texcoords = np.array(
                [
                    [0.0, 0.0],
                    [1.0, 0.0],
                    [0.5, 1.0],
                ],
                dtype=np.float32,
            )
            vao.add_vbo(
                location=2,
                data=texcoords,
                ncomponents=texcoords.shape[1],
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

        self.shapes.append(
            Part(vao, GL.GL_TRIANGLES, len(vertices)),
        )
