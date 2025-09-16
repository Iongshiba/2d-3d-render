import numpy as np

from OpenGL import GL

from libs.buffer import VBO, VAO, EBO
from libs.shader import Shader, ShaderProgram


class Tetrahedron:
    def __init__(self, vertex_file, fragment_file):
        self.vertices = [
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.0, 0.5, 0.0],
            [0.0, 0.0, 0.5],
        ]
        self.colors = [
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
        ]
