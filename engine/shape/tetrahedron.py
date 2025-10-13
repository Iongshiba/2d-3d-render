import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Tetrahedron(Shape):
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
            Vertex(-1.0,  0.0, -1.0),
            Vertex( 0.0,  0.0,  1.0),
            Vertex( 1.0,  0.0, -1.0),
            Vertex( 0.0,  1.0,  0.0),
        ]
        indices = np.array([
            0, 1, 2,
            0, 2, 3,
            1, 0, 3,
            2, 1, 3,
        ], dtype=np.int32)
        indices = indices.reshape(-1, 3)
        norms = np.zeros((len(vertices), 3), dtype=np.float32)
        centroid = sum(v.vertex for v in vertices) / len(vertices)
        for tri in indices:
            ia, ib, ic = tri
            a, b, c = vertices[ia].vertex, vertices[ib].vertex, vertices[ic].vertex
            n = np.cross(b - a, c - a)
            n /= np.linalg.norm(n)
            face_center = (a + b + c) / 3.0
            if np.dot(n, face_center - centroid) < 0:
                n = -n

            norms[ia] += n
            norms[ib] += n
            norms[ic] += n

        norms = np.array(norms, dtype=np.float32)
        # fmt: on

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

        self.shapes.append(
            Part(vao, GL.GL_TRIANGLES, len(vertices), indices.size),
        )
