from OpenGL import GL


class Shader:
    def __init__(self, source, typ=None):
        self.source = source
        self.typ = typ

        if typ is None:
            typ_name = source.split(".")[-1]
            match typ_name:
                case "vert":
                    self.typ = GL.GL_VERTEX_SHADER
                case "frag":
                    self.typ = GL.GL_FRAGMENT_SHADER
                case _:
                    raise ValueError(f"Invalid file extension {typ_name}")

        self.shader = self.compile_shader(source, typ)

    @staticmethod
    def compile_shader(source, typ):
        with open(source, "r") as f:
            code = f.read()
            shader = GL.glCreateShader(typ)
            GL.glShaderSource(shader, code)
            GL.glcompile_shader(shader)

        if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
            log = GL.glGetShaderInfoLog(shader).decode()
            raise RuntimeError(log)

        return shader


class Program:
    def __init__(self):
        self.shaders = {}
        self.program = GL.glCreateProgram()

    def add_shader(self, shader):
        self.shaders[shader.source] = shader.shader

    def build(self):
        for _, shader in self.shaders.items():
            GL.glAttachShader(self.program, shader)
        GL.glLinkProgram(self.program)
        for _, shader in self.shaders.items():
            GL.glDeleteShader(shader)

        if GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS) != GL.GL_TRUE:
            log = GL.glGetProgramInfoLog(self.program).decode()
            raise RuntimeError(log)

    def activate(self):
        GL.glUseProgram(self.program)

    def deactivate(self):
        GL.glUseProgram(0)
