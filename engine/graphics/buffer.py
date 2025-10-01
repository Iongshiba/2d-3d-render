from OpenGL import GL


# fmt: off
class VAO:
    def __init__(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        GL.glBindVertexArray(0)
        self.vbos = {}
        self.ebo = None

    def add_vbo(self, location, data, ncomponents, dtype, normalized, stride, offset):
        self.activate()

        # Create VBO
        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
        self.vbos[location] = vbo

        # Bind VBO
        GL.glVertexAttribPointer(
            location,
            ncomponents,
            dtype,
            normalized,
            stride,
            offset,
        )
        GL.glEnableVertexAttribArray(
            location
        )  # the number of this call match the number of (layout = n) in .vert file

        self.deactivate()

    def add_ebo(self, data):
        self.activate()

        ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, data, GL.GL_STATIC_DRAW)
        # Store reference; keep EBO bound while VAO is active so the binding is recorded in VAO state
        self.ebo = ebo

        # Deactivate VAO first so unbinding the EBO (if desired) won't clear the VAO's EBO binding
        self.deactivate()

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
