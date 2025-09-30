from OpenGL import GL


# class VBO:
#     def __init__(
#         self,
#         location,
#         data,
#         ncomponents=3,
#         dtype=GL.GL_FLOAT,
#         normalized=False,
#         stride=0,
#         offset=None,
#     ):
#         self.vbo = GL.glGenBuffers(1)

#         self.activate()
#         GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
#         self.deactivate()

#         self.location = location
#         self.data = data
#         self.ncomponents = ncomponents
#         self.dtype = dtype
#         self.normalized = normalized
#         self.stride = stride
#         self.offset = offset

#     def activate(self):
#         GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

#     def deactivate(self):
#         GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)


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
#         GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

# fmt: off
class VAO:
    def __init__(self):
        self.vao = GL.glGenVertexArrays(1)
        self.vbos = {}
        self.ebo = None

    def add_vbo(self, location, data, ncomponents, dtype, normalized, stride, offset):
        self.activate()

        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        self.vbos[vbo.location] = vbo

        GL.glVertexAttribPointer(
            location,
            ncomponents,
            dtype,
            normalized,
            stride,
            offset,
        )
        GL.glEnableVertexAttribArray(
            vbo.location
        )  # the number of this call match the number of (layout = n) in .vert file

        self.deactivate()

    def add_ebo(self, ebo):
        self.activate()
        ebo.activate()  # bind EBO to the currently active VAO

        # Store reference; keep EBO bound while VAO is active so the binding is recorded in VAO state
        self.ebo = ebo

        # Deactivate VAO first so unbinding the EBO (if desired) won't clear the VAO's EBO binding
        self.deactivate()
        # Optional: unbind element array buffer to avoid leaking global binding (doesn't affect VAO's stored state)
        ebo.deactivate()

    def __del__(self):
        GL.glDeleteVertexArrays(1, [self.vao])
        vbos = list(self.vbos.values())
        if vbos:
            GL.glDeleteBuffers(len(vbos), vbos)
        if self.ebo is not None:
            GL.glDeleteBuffers(1, [self.ebo.ebo])

    def activate(self):
        GL.glBindVertexArray(self.vao)  # activated

    def deactivate(self):
        GL.glBindVertexArray(0)  # activated
