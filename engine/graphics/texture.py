import numpy as np

from OpenGL import GL


class Texture2D:
    def __init__(self):
        self.tex = GL.glGenTextures(1)

        # fmt: off
        self.activate()
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        self.deactivate()

    def add_texture(
        self,
        data,
        width,
        height,
        target=GL.GL_TEXTURE_2D,
        mipmap_level=0,
        texture_format=GL.GL_RGB,
        border=0,
        dtype=np.byte,
    ):
        self.activate()
        GL.glTexImage2D(
            target, mipmap_level, texture_format, width, height, border, dtype, data
        )
        self.deactivate()

    def activate(self):
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex)

    def deactivate(self):
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
