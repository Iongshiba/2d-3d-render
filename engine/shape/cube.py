import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# fmt: off
class Cube(Shape):
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

        vertices = [
            # back square with normal outside
            Vertex(-0.5, 0.5, -0.5),
            Vertex(0.5, 0.5, -0.5),
            Vertex(-0.5, -0.5, -0.5),
            Vertex(0.5, -0.5, -0.5),
            # front square
            Vertex(-0.5, 0.5, 0.5),
            Vertex(0.5, 0.5, 0.5),
            Vertex(-0.5, -0.5, 0.5),
            Vertex(0.5, -0.5, 0.5),
        ]

        left_norms = np.array([-1.0, 0.0, 0.0], dtype=np.float32)
        right_norms = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        front_norms = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        back_norms = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        top_norms = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        bottom_norms = np.array([0.0, -1.0, 0.0], dtype=np.float32)

        print(np.mean([left_norms, back_norms, top_norms]),)

        norms = np.array([
            np.mean([left_norms, back_norms, top_norms], axis=0),
            np.mean([right_norms, back_norms, top_norms], axis=0),
            np.mean([left_norms, back_norms, bottom_norms], axis=0),
            np.mean([right_norms, back_norms, bottom_norms], axis=0),
            np.mean([left_norms, top_norms, top_norms], axis=0),
            np.mean([right_norms, top_norms, top_norms], axis=0),
            np.mean([left_norms, top_norms, bottom_norms], axis=0),
            np.mean([right_norms, top_norms, bottom_norms], axis=0),
        ], dtype=np.float32)
        
        coords = vertices_to_coords(vertices)
        colors = vertices_to_colors(vertices)

        indices = np.array([
            # back with normal go out
            0, 2, 1,
            3, 1, 2,
            # front with normal go out
            4, 5, 6,
            7, 6, 5,
            # left
            4, 6, 0,
            2, 0, 6,
            # right
            5, 1, 7,
            3, 7, 1,
            # front
            6, 7, 2,
            3, 2, 7,
            # back
            0, 1, 4,
            5, 4, 1,
        ], dtype=np.uint32)

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
        vao.add_vbo(
            location=2, 
            data=norms,
            ncomponents=norms.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_ebo(
            indices
        )

        self.shapes.extend(
            [Part(vao, GL.GL_TRIANGLES, coords.shape[0], indices.shape[0])]
        )
