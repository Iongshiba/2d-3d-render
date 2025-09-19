import numpy as np

from OpenGL import GL

from libs.buffer import VBO, VAO, EBO
from libs.shader import Shader, ShaderProgram


# fmt: off
class Triangle:
    def __init__(self, vertex_file, fragment_file):
        self.vertices = [
            [-1, -1, 0.0],
            [1, -1, 0.0],
            [0.0, 1, 0.0],
        ]
        self.colors = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.colors = np.array(self.colors, dtype=np.float32)

        vertex_vbo = VBO(0, self.vertices)
        color_vbo = VBO(1, self.colors)
        self.vao = VAO()
        self.vao.add_vbo(vertex_vbo)
        self.vao.add_vbo(color_vbo)

        vertex_shader = Shader(vertex_file)
        fragment_shader = Shader(fragment_file)
        self.shader_program = ShaderProgram()

        self.shader_program.add_shader(vertex_shader)
        self.shader_program.add_shader(fragment_shader)
        self.shader_program.build()


        self.delta = 0.00005
        self.alpha = 1.0
        self.transform_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32) # should create a copy for each transformation
        self.transform_loc = GL.glGetUniformLocation(self.shader_program.program, "transform")

        # set an initial scale
        self.shader_program.activate()
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, self.transform_matrix)
        self.shader_program.deactivate()

    def transform(self, fn, *args):
        if self.alpha <= -1 or self.alpha >= 1:
            self.delta *= -1
        self.alpha += self.delta
        fn(*args)

    def scale(self, factor=1):
        self.transform_matrix[0, 0] = np.float32(factor)
        self.transform_matrix[1, 1] = np.float32(factor)
        self.transform_matrix[2, 2] = np.float32(factor)
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, self.transform_matrix)

    def translate(self):
        self.transform_matrix[0, 3] = self.alpha
        self.transform_matrix[1, 3] = self.alpha
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, self.transform_matrix)

    def rotate(self, axis='x'):
        rotation = np.array([
            [np.cos(self.alpha), -np.sin(self.alpha)],
            [np.sin(self.alpha), np.cos(self.alpha)],
        ], dtype=np.float32)
        anchor = (0, 0)
        if axis == 'x':
            anchor = (0, 0)
        elif axis == 'y':
            anchor = (1, 1)
        elif axis == 'z':
            anchor = (2, 2)
        self.transform_matrix[anchor[0] : anchor[0] + 2, anchor[1] : anchor[1] + 2] = rotation
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, self.transform_matrix)

# fmt: on
    def draw(self):
        self.vao.activate()
        self.shader_program.activate()

        # transformation
        self.transform(self.scale, 0.25)
        self.transform(self.translate)
        self.transform(self.rotate, 'x')

        # clear screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)  # Doesn't require EBO

        self.shader_program.deactivate()
        self.vao.deactivate()
