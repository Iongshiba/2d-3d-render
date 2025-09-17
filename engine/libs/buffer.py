from OpenGL import GL


class VBO:
    def __init__(
        self,
        location,
        data,
        ncomponents=3,
        dtype=GL.GL_FLOAT,
        normalized=False,
        stride=0,
        offset=None,
    ):
        self.vbo = GL.glGenBuffers(1)

        self.activate()
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
        self.deactivate()

        self.location = location
        self.data = data
        self.ncomponents = ncomponents
        self.dtype = dtype
        self.normalized = normalized
        self.stride = stride
        self.offset = offset

    def activate(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

    def deactivate(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)


class EBO:
    def __init__(
        self,
        indices,
    ):
        self.ebo = GL.glGenBuffers(1)

        self.activate()
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices, GL.GL_STATIC_DRAW)
        self.deactivate()

        self.indices = indices

    def activate(self):
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

    def deactivate(self):
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)


class VAO:
    def __init__(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        GL.glBindVertexArray(0)
        self.vbos = {}
        self.ebo = None

    def add_vbo(self, vbo):
        self.activate()
        vbo.activate()

        # location = GL.glGetAttribLocation(self.shader.render_idx, name)
        GL.glVertexAttribPointer(
            vbo.location,
            vbo.ncomponents,
            vbo.dtype,
            vbo.normalized,
            vbo.stride,
            vbo.offset,
        )
        GL.glEnableVertexAttribArray(vbo.location)
        self.vbos[vbo.location] = vbo.vbo

        vbo.deactivate()
        self.deactivate()

    def add_ebo(self, ebo):
        self.activate()
        ebo.activate()

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        self.ebo = ebo

        ebo.deactivate()
        self.deactivate()

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.vao])
        vbos = list(self.vbos.values())
        GL.glDeleteBuffers(len(vbos), [vbos])
        if self.ebo is not None:
            GL.glDeleteBuffers(1, [self.ebo])

    def activate(self):
        GL.glBindVertexArray(self.vao)  # activated

    def deactivate(self):
        GL.glBindVertexArray(0)  # activated
