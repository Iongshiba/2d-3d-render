import numpy as np

from OpenGL import GL

from libs.vertex import Vertex
from libs.buffer import VBO, VAO, EBO
from libs.shader import Shader, ShaderProgram

# fmt: off
class Cube:
    def __init__(self, vertex_file, fragment_file):
        self.vertices = [
            # bottom square
            Vertex(-0.5, 0.5, -0.5),
            Vertex(0.5, 0.5, -0.5),
            Vertex(-0.5, -0.5, -0.5),
            Vertex(0.5, -0.5, -0.5),
            # top square
            Vertex(-0.5, 0.5, 0.5),
            Vertex(0.5, 0.5, 0.5),
            Vertex(-0.5, -0.5, 0.5),
            Vertex(0.5, -0.5, 0.5),
        ]
        self.indexes = [

        ]

        coord_vbo = VBO(0, self.vertices, stride=3, offset=0)
        color_vbo = VBO(1, self.vertices, stride=3, offset=3)
        coord_ebo = EBO()
        self.vao = VAO()

        self.vao.add_vbo(coord_vbo)
        self.vao.add_vbo(color_vbo)

        vertex_shader = Shader(vertex_file)
        fragment_shader = Shader(fragment_file)
        self.shader_program = ShaderProgram()

        self.shader_program.add_shader(vertex_shader)
        self.shader_program.add_shader(fragment_shader)
        self.shader_program.build()
