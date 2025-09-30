import numpy as np

from OpenGL import GL

from graphics.buffer import VBO, VAO, EBO
from graphics.shader import Shader, ShaderProgram


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
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)

        vertex_shader = Shader(vertex_file)
        fragment_shader = Shader(fragment_file)
        self.shader_program = ShaderProgram()
