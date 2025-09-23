from __future__ import annotations

from OpenGL import GL

try:
    from .config import (
        EngineConfig,
        ShapeType,
        ColorMode,
        ShadingModel,
        TextureMode,
        RenderMode,
    )
    from .registry import ShapeRegistry
except Exception:  # fallback when executed as a script
    from config import (
        EngineConfig,
        ShapeType,
        ColorMode,
        ShadingModel,
        TextureMode,
        RenderMode,
    )
    from registry import ShapeRegistry


class Renderer:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.shape = self._create_shape(config)

        # GL state (simple defaults)
        GL.glViewport(0, 0, config.width, config.height)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CW)
        GL.glClearColor(0.1, 0.1, 0.12, 1.0)

        # Render mode placeholder (wireframe later)
        if config.render_mode == RenderMode.FILL:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

        self._apply_mode_uniforms()

    def _apply_mode_uniforms(self):
        program = getattr(self.shape, "shader_program", None)
        if program is None:
            return
        program.activate()
        try:
            loc = GL.glGetUniformLocation(program.program, "uColorMode")
            if loc != -1:
                GL.glUniform1i(loc, int(self.config.color_mode.value))
            loc = GL.glGetUniformLocation(program.program, "uFlatColor")
            if loc != -1:
                r, g, b = self.config.flat_color
                GL.glUniform3f(loc, float(r), float(g), float(b))
            loc = GL.glGetUniformLocation(program.program, "uShadingModel")
            if loc != -1:
                GL.glUniform1i(loc, int(self.config.shading.value))
            loc = GL.glGetUniformLocation(program.program, "uTextureMode")
            if loc != -1:
                GL.glUniform1i(loc, int(self.config.texture.value))
        finally:
            program.deactivate()

    def _create_shape(self, cfg: EngineConfig):
        return ShapeRegistry.create(cfg.shape, cfg)

    def draw(self, app=None):
        # Provide uniforms for color/shading/texture modes if shaders support them
        program = getattr(self.shape, "shader_program", None)
        if program is not None:
            program.activate()
            try:
                loc = GL.glGetUniformLocation(program.program, "uColorMode")
                if loc != -1:
                    GL.glUniform1i(loc, int(self.config.color_mode.value))
                loc = GL.glGetUniformLocation(program.program, "uFlatColor")
                if loc != -1:
                    r, g, b = self.config.flat_color
                    GL.glUniform3f(loc, float(r), float(g), float(b))
                loc = GL.glGetUniformLocation(program.program, "uShadingModel")
                if loc != -1:
                    GL.glUniform1i(loc, int(self.config.shading.value))
                loc = GL.glGetUniformLocation(program.program, "uTextureMode")
                if loc != -1:
                    GL.glUniform1i(loc, int(self.config.texture.value))
            finally:
                program.deactivate()

        # Delegate drawing to the shape (it handles its own transforms)
        try:
            self.shape.draw(app)
        except TypeError:
            self.shape.draw()
