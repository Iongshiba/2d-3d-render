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
        gradient_mode=None,
        gradient_start=(1.0, 0.0, 0.0),
        gradient_end=(0.0, 0.0, 1.0),
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
        
        # Apply gradient colors if gradient_mode is specified
        # if gradient_mode:
        #     from utils import generate_gradient_colors
        #     colors = generate_gradient_colors(vertices, gradient_mode, gradient_start, gradient_end)
        # else:
        #     colors = vertices_to_colors(vertices)
        colors = self._apply_color_override(vertices_to_colors(vertices), color)

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
        
        if texture_file:
            # Cube texture coordinates (one UV coordinate per vertex)
            texcoords = np.array([
                [0.0, 1.0],  # back-top-left
                [1.0, 1.0],  # back-top-right
                [0.0, 0.0],  # back-bottom-left
                [1.0, 0.0],  # back-bottom-right
                [0.0, 1.0],  # front-top-left
                [1.0, 1.0],  # front-top-right
                [0.0, 0.0],  # front-bottom-left
                [1.0, 0.0],  # front-bottom-right
            ], dtype=np.float32)
            vao.add_vbo(
                location=3,
                data=texcoords,
                ncomponents=2,
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
