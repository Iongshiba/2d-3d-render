from .shader import Shader  # relative import within package
from OpenGL import GL
import cv2


class VAO:
    def __init__(self):

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        GL.glBindVertexArray(0)
        self.vbo = {}
        self.ebo = None

    def add_vbo(
        self,
        location,
        data,
        ncomponents=3,
        dtype=GL.GL_FLOAT,
        normalized=False,
        stride=0,
        offset=None,
    ):
        self.activate()

        buffer_idx = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer_idx)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
        # location = GL.glGetAttribLocation(self.shader.render_idx, name)
        GL.glVertexAttribPointer(
            location, ncomponents, dtype, normalized, stride, offset
        )
        GL.glEnableVertexAttribArray(location)
        self.vbo[location] = buffer_idx

        self.deactivate()

    def add_ebo(self, indices):
        self.activate()

        self.ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices, GL.GL_STATIC_DRAW)

        self.deactivate()

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.vao])
        GL.glDeleteBuffers(1, list(self.vbo.values()))
        if self.ebo is not None:
            GL.glDeleteBuffers(1, [self.ebo])

    def activate(self):
        GL.glBindVertexArray(self.vao)  # activated

    def deactivate(self):
        GL.glBindVertexArray(0)  # activated
