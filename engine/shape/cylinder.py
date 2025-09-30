import numpy as np

from OpenGL import GL

from graphics.vertex import Vertex
from shape.base import Shape, ShapeCandidate

# fmt: off
class Cylinder(Shape):
    def __init__(self, vertex_file, fragment_file, height, radius, sector):
        super().__init__(vertex_file, fragment_file)

        self.height = height
        self.radius = radius
        self.sector = sector

        top_circle = [Vertex(0, 0, height / 2.0)]
        bottom_circle = [Vertex(0, 0, -height / 2.0)]
        for point in range(1, sector + 1):
            angle = 2.0 * np.pi * point / sector
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            top_circle.append(Vertex(x, y, height / 2.0))
            bottom_circle.append(Vertex(x, y, -height / 2.0))
        top_circle.append(top_circle[1])
        bottom_circle.append(bottom_circle[1])

        top_coords = np.array(
            [o.vertex.flatten() for o in top_circle], dtype=np.float32
        )
        top_colors = np.array(
            [o.color.flatten() for o in top_circle], dtype=np.float32
        )
        bottom_coords = np.array(
            [o.vertex.flatten() for o in bottom_circle], dtype=np.float32
        )
        bottom_colors = np.array(
            [o.color.flatten() for o in bottom_circle], dtype=np.float32
        )
        side_coords = np.empty((top_coords.shape[0] + bottom_coords.shape[0] - 2, top_coords.shape[1]), dtype=np.float32)
        side_coords[0::2] = top_coords[1:]
        side_coords[1::2] = bottom_coords[1:]
        side_colors = np.empty((top_colors.shape[0] + bottom_colors.shape[0] - 2, top_colors.shape[1]), dtype=np.float32)
        side_colors[0::2] = top_colors[1:]
        side_colors[1::2] = bottom_colors[1:]

        bottom_coords *= -1

        self.shape_candidates = [
            ShapeCandidate(0, GL.GL_TRIANGLE_FAN, {0: top_coords, 1: top_colors}),
            ShapeCandidate(1, GL.GL_TRIANGLE_FAN, {0: bottom_coords, 1: bottom_colors}),
            ShapeCandidate(2, GL.GL_TRIANGLE_STRIP, {0: side_coords, 1: side_colors}),
        ]

        self.setup_buffers()
