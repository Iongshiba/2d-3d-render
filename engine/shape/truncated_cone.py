import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


# fmt: on
class TruncatedCone(Shape):
    def __init__(
        self,
        height: float,
        top_radius: float,
        bottom_radius: float,
        sector: int,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ):
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.height = height
        self.top_radius = top_radius
        self.bottom_radius = bottom_radius
        self.sector = sector

        top_circle = [Vertex(0, 0, height / 2.0)]
        bottom_circle = [Vertex(0, 0, -height / 2.0)]
        vector_up = top_circle[0].vertex - bottom_circle[0].vertex
        side_norms = []
        for point in range(1, sector + 1):
            angle = 2.0 * np.pi * point / sector
            x_top = top_radius * np.cos(angle)
            y_top = top_radius * np.sin(angle)
            x_bottom = bottom_radius * np.cos(angle)
            y_bottom = bottom_radius * np.sin(angle)

            top_circle.append(Vertex(x_top, y_top, height / 2.0))
            bottom_circle.append(Vertex(x_bottom, y_bottom, -height / 2.0))

            # Calculate Norm
            side_norms.extend(
                [
                    bottom_circle[-1].vertex - bottom_circle[0].vertex,
                    top_circle[-1].vertex - top_circle[0].vertex,
                ]
            )

        top_circle.append(top_circle[1])
        bottom_circle.append(bottom_circle[1])
        side_norms.extend(
            [
                side_norms[0],
                side_norms[1],
            ]
        )

        top_coords = vertices_to_coords(top_circle)
        top_colors = vertices_to_colors(top_circle)
        top_norms = np.tile(vector_up, len(top_coords))
        bottom_coords = vertices_to_coords(bottom_circle)
        bottom_colors = vertices_to_colors(bottom_circle)
        bottom_norms = np.tile(-vector_up, len(bottom_coords))
        side_norms = np.array(side_norms, dtype=np.float32)

        side_coords = np.empty(
            (top_coords.shape[0] + bottom_coords.shape[0] - 2, top_coords.shape[1]),
            dtype=np.float32,
        )
        side_coords[0::2] = bottom_coords[1:]
        side_coords[1::2] = top_coords[1:]
        side_colors = np.empty(
            (top_colors.shape[0] + bottom_colors.shape[0] - 2, top_colors.shape[1]),
            dtype=np.float32,
        )
        side_colors[0::2] = bottom_colors[1:]
        side_colors[1::2] = top_colors[1:]

        top_coords[1:] = top_coords[:0:-1]
        top_colors[1:] = top_colors[:0:-1]

        top_vao = VAO()
        top_vao.add_vbo(
            location=0,
            data=top_coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        top_vao.add_vbo(
            location=1,
            data=top_colors,
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

        bottom_vao = VAO()
        bottom_vao.add_vbo(
            location=0,
            data=bottom_coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        bottom_vao.add_vbo(
            location=1,
            data=bottom_colors,
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
        side_vao.add_vbo(
            location=2,
            data=side_norms,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        self.shapes.extend(
            [
                Part(top_vao, GL.GL_TRIANGLE_FAN, top_coords.shape[0]),
                Part(bottom_vao, GL.GL_TRIANGLE_FAN, bottom_coords.shape[0]),
                Part(side_vao, GL.GL_TRIANGLE_STRIP, side_coords.shape[0]),
            ]
        )
