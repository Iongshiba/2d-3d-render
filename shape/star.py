import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Star(Shape):
    def __init__(
        self,
        wing: int,
        outer_radius: float,
        inner_radius: float,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ) -> None:
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        angles = np.linspace(0, 2 * np.pi, wing * 2 + 1)
        vertices = [Vertex(0.0, 0.0, 0.0)]
        vertices.extend(
            [
                (
                    Vertex(
                        outer_radius * np.cos(angle), outer_radius * np.sin(angle), 0.0
                    )
                    if i % 2 == 0
                    else Vertex(
                        inner_radius * np.cos(angle), inner_radius * np.sin(angle), 0.0
                    )
                )
                for i, angle in enumerate(angles)
            ]
        )

        coords = vertices_to_coords(vertices)
        colors = self._apply_color_override(vertices_to_colors(vertices), color)

        # Normals for 2D star (pointing in +Z direction)
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
            # Texture coordinates for star (center at 0.5, 0.5, then radial mapping)
            texcoords = np.zeros((len(vertices), 2), dtype=np.float32)
            texcoords[0] = [0.5, 0.5]  # Center
            for i, angle in enumerate(angles):
                radius_factor = outer_radius if i % 2 == 0 else inner_radius
                max_radius = max(outer_radius, inner_radius)
                texcoords[i + 1] = [
                    0.5 + 0.5 * (radius_factor / max_radius) * np.cos(angle),
                    0.5 + 0.5 * (radius_factor / max_radius) * np.sin(angle),
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
