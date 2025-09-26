from __future__ import annotations

from OpenGL import GL

from config import EngineConfig
from core.enums import ColorMode, RenderMode, ShadingModel, TextureMode
from shape.factory import ShapeFactory
from rendering.strategies import (
    FillRenderingStrategy,
    RenderingStrategy,
    WireframeRenderingStrategy,
)
from utils import shader_program, vao_context


class Renderer:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.shape = ShapeFactory.create_shape(config.shape, config)

        # GL state (simple defaults)
        GL.glViewport(0, 0, self.config.width, self.config.height)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
        GL.glClearColor(0.1, 0.1, 0.12, 1.0)

        # TODO Implement Rendering strategy for Wireframe and fill
        self._strategies: dict[RenderMode, RenderingStrategy] = {
            RenderMode.FILL: FillRenderingStrategy(),
            RenderMode.WIREFRAME: WireframeRenderingStrategy(),
        }
        self._strategy: RenderingStrategy = self._strategies[self.config.render_mode]
        self._strategy.setup_gl_state(self.config)

        self._apply_mode_uniforms()

    def _apply_mode_uniforms(self):
        program = getattr(self.shape, "shader_program", None)
        if program is None:
            return
        with shader_program(program):
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

    def draw(self, app=None):
        # Provide uniforms for color/shading/texture modes if shaders support them
        self._apply_mode_uniforms()
        self._strategy.apply_to_shape(self.shape)

        # Delegate drawing to the shape (it handles its own transforms)
        try:
            self.shape.draw(app)
        except TypeError:
            self.shape.draw()

    # TODO haven't use yet
    def set_render_mode(self, mode: RenderMode) -> None:
        if mode not in self._strategies:
            raise ValueError(f"Unsupported render mode: {mode!r}")
        self.config.render_mode = mode
        self._strategy = self._strategies[mode]
        self._strategy.setup_gl_state(self.config)
        self._apply_mode_uniforms()
