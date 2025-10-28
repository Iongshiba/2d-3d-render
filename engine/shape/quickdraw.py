import numpy as np

from OpenGL import GL

from utils import *
from graphics.buffer import VAO
from graphics.vertex import Vertex
from shape.base import Shape, Part


# fmt: off
class QuickDraw(Shape):
    def __init__(
        self,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ):
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        vertices = []
        indices = []
        norms = []

        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)
        indices = np.array(indices, dtype=np.int32)
        norms = np.array(norms, dtype=np.float32)

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
        vao.add_vbo(
            location=2,
            data=norms,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_ebo(
            indices,
        )

        self.shapes.extend(
            [
                Part(
                    vao,
                    GL.GL_TRIANGLE_STRIP,
                    colors.shape[0],
                    indices.shape[0],
                ),
            ]
        )
