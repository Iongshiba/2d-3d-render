import numpy as np

from OpenGL import GL

from libs.buffer import VBO, VAO, EBO
from libs.shader import Shader, ShaderProgram


class Triangle:
    def __init__(self, vertex_file, fragment_file):
        self.vertices = [
            [-1, -1, 0.0],
            [1, -1, 0.0],
            [0.0, 1, 0.0],
        ]
        self.colors = [
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ]
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)

        vertex_shader = Shader(vertex_file)
        fragment_shader = Shader(fragment_file)
        self.shader_program = ShaderProgram()

        vertex_vbo = VBO(0, self.vertices)
        color_vbo = VBO(1, self.colors)
        self.vao = VAO()

        self.vao.add_vbo(vertex_vbo)
        self.vao.add_vbo(color_vbo)

        self.shader_program.add_shader(vertex_shader)
        self.shader_program.add_shader(fragment_shader)
        self.shader_program.build()

    def draw(self):
        self.vao.activate()
        self.shader_program.activate()
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)  # Doesn't require EBO
        self.shader_program.deactivate()
        self.vao.deactivate()
