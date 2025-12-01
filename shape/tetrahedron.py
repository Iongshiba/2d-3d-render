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
        ):
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        # fmt: off
        vertices = [
            Vertex(-1.0,  0.0, -1.0),  # 0
            Vertex( 0.0,  0.0,  1.0),  # 1
            Vertex( 1.0,  0.0, -1.0),  # 2
            Vertex( 0.0,  1.0,  0.0),  # 3
        ]
        indices = np.array([
            0, 1, 2,  # Bottom face
            0, 2, 3,  # Right face
            1, 0, 3,  # Left face
            2, 1, 3,  # Front face
        ], dtype=np.int32)
        # fmt: on
        
        # Calculate face normals
        face_normals = [
            np.array([0.0, -1.0, 0.0]),              # Face 1 (0, 1, 2) - bottom
            np.array([0.0, -0.707, 0.707]),          # Face 2 (0, 2, 3) - right
            np.array([0.816, -0.408, -0.408]),       # Face 3 (1, 0, 3) - left
            np.array([-0.816, 0.408, -0.408]),       # Face 4 (2, 1, 3) - front
        ]
        
        # Calculate per-vertex normals by averaging adjacent face normals
        # Vertex 0 is in faces: 0, 1, 2
        # Vertex 1 is in faces: 0, 2, 3
        # Vertex 2 is in faces: 0, 1, 3
        # Vertex 3 is in faces: 1, 2, 3
        vertex_normals = [
            (face_normals[0] + face_normals[1] + face_normals[2]) / 3.0,  # Vertex 0
            (face_normals[0] + face_normals[2] + face_normals[3]) / 3.0,  # Vertex 1
            (face_normals[0] + face_normals[1] + face_normals[3]) / 3.0,  # Vertex 2
            (face_normals[1] + face_normals[2] + face_normals[3]) / 3.0,  # Vertex 3
        ]
        
        # Normalize the averaged normals
        normals = np.array([
            vertex_normals[0] / np.linalg.norm(vertex_normals[0]),
            vertex_normals[1] / np.linalg.norm(vertex_normals[1]),
            vertex_normals[2] / np.linalg.norm(vertex_normals[2]),
            vertex_normals[3] / np.linalg.norm(vertex_normals[3]),
        ], dtype=np.float32)

        coords = vertices_to_coords(vertices)
        colors = self._apply_color_override(vertices_to_colors(vertices), color)
        
        # Dummy texture coordinates (required by shader even if not used)
        texcoords = np.array([
            [0.0, 0.0],  # Vertex 0
            [1.0, 0.0],  # Vertex 1
            [0.5, 1.0],  # Vertex 2
            [0.5, 0.5],  # Vertex 3
        ], dtype=np.float32)

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
            data=normals,
            ncomponents=normals.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
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
            indices,
        )

        self.shapes.append(
            Part(vao, GL.GL_TRIANGLES, len(vertices), indices.size),
        )
