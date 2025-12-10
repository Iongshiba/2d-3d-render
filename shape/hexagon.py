import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Hexagon(Shape):
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

        angles = np.linspace(0, 2 * np.pi, 7)
        vertices = [Vertex(0.0, 0.0, 0.0)]
        vertices.extend(
            [
                Vertex(
                    np.cos(angle),
                    np.sin(angle),
                    0.0,
                )
                for angle in angles
            ]
        )

        coords = vertices_to_coords(vertices)
        colors = self._apply_color_override(vertices_to_colors(vertices), color)

        # Normals for 2D hexagon (pointing in +Z direction)
        normals = np.tile([0.0, 0.0, 1.0], (len(vertices), 1)).astype(np.float32)

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
            data=normals,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        if texture_file:
            # Texture coordinates for hexagon (center at 0.5, 0.5, then radial mapping)
            texcoords = np.zeros((len(vertices), 2), dtype=np.float32)
            texcoords[0] = [0.5, 0.5]  # Center
            for i, angle in enumerate(angles):
                texcoords[i + 1] = [
                    0.5 + 0.5 * np.cos(angle),
                    0.5 + 0.5 * np.sin(angle),
                ]
            vao.add_vbo(
                location=3,
                data=texcoords,
                ncomponents=texcoords.shape[1],
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

        self.shapes.extend([Part(vao, GL.GL_TRIANGLE_FAN, len(vertices))])
