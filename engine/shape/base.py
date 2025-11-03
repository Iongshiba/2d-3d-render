import numpy as np

from pathlib import Path
from OpenGL import GL

from utils import *
from config import _SHAPE_FRAGMENT_PATH, _SHAPE_VERTEX_PATH, ShadingModel
from graphics.buffer import VAO
from graphics.shader import Shader, ShaderProgram
from graphics.texture import Texture2D


class Part:
    def __init__(
        self,
        vao: VAO,
        draw_mode: GL.constant.IntConstant,
        vertex_num: int,
        index_num: int | None = None,
    ):
        self.vao = vao
        self.draw_mode = draw_mode
        self.vertex_num = vertex_num
        self.index_num = index_num


# fmt: on
class Shape:
    def __init__(self, vertex_file: str, fragment_file: str):
        # Shaders
        if not vertex_file:
            vertex_file = _SHAPE_VERTEX_PATH
        if not fragment_file:
            fragment_file = _SHAPE_FRAGMENT_PATH

        vertex_shader = Shader(vertex_file)
        fragment_shader = Shader(fragment_file)
        self.shader_program = ShaderProgram()
        self.shader_program.add_shader(vertex_shader)
        self.shader_program.add_shader(fragment_shader)
        self.shader_program.build()

        # Geometry containers
        self.shapes: list[Part] = []

        self.identity = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )

        self.texture = None
        self.shading_mode = ShadingModel.PHONG

        # fmt: off
        self.transform_loc = GL.glGetUniformLocation(self.shader_program.program, "transform")
        self.camera_loc = GL.glGetUniformLocation(self.shader_program.program, "camera")
        self.project_loc = GL.glGetUniformLocation(self.shader_program.program, "project")
        self.use_texture_loc = GL.glGetUniformLocation(self.shader_program.program, "use_texture")
        self.texture_data_loc = GL.glGetUniformLocation(self.shader_program.program, "textureData")
        self.light_color_loc = GL.glGetUniformLocation(self.shader_program.program, "lightColor")
        self.light_coord_loc = GL.glGetUniformLocation(self.shader_program.program, "lightCoord")
        self.camera_coord_loc = GL.glGetUniformLocation(self.shader_program.program, "cameraCoord")
        self.shading_mode_loc = GL.glGetUniformLocation(self.shader_program.program, "shadingMode")

        self.shader_program.activate()
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, self.identity)
        GL.glUniformMatrix4fv(self.camera_loc, 1, GL.GL_TRUE, self.identity)
        GL.glUniformMatrix4fv(self.project_loc, 1, GL.GL_TRUE, self.identity)
        GL.glUniform1i(self.use_texture_loc, True)
        GL.glUniform1i(self.texture_data_loc, 0)
        if self.shading_mode_loc != -1:
            GL.glUniform1i(self.shading_mode_loc, self.shading_mode.value)
        self.shader_program.deactivate()

    def draw(self):
        self.shader_program.activate()
        # Set use_texture based on whether texture exists
        GL.glUniform1i(self.use_texture_loc, 1 if self.texture else 0)
        for shape in self.shapes:
            vao = shape.vao
            vao.activate()
            if self.texture:
                self.texture.activate()
            # fmt: off
            if vao.ebo is not None:
                GL.glDrawElements(
                    shape.draw_mode, shape.index_num, GL.GL_UNSIGNED_INT, None
                )
            else:
                GL.glDrawArrays(
                    shape.draw_mode, 0, shape.vertex_num
                )
            if self.texture:
                self.texture.deactivate()
            vao.deactivate()
        self.shader_program.deactivate()

    def transform(
        self,
        project_matrix: np.ndarray,
        view_matrix: np.ndarray,
        model_matrix: np.ndarray,
    ):
        self.shader_program.activate()
        GL.glUniformMatrix4fv(self.project_loc, 1, GL.GL_TRUE, project_matrix)
        GL.glUniformMatrix4fv(self.camera_loc, 1, GL.GL_TRUE, view_matrix)
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, model_matrix)
        self.shader_program.deactivate()

    def lighting(
        self,
        light_color: np.ndarray,
        light_position: np.ndarray,
        camera_position: np.ndarray,
    ):
        self.shader_program.activate()
        GL.glUniform3fv(self.light_color_loc, 1, light_color)
        GL.glUniform3fv(self.light_coord_loc, 1, light_position)
        GL.glUniform3fv(self.camera_coord_loc, 1, camera_position)
        self.shader_program.deactivate()

    def set_shading_mode(self, shading: ShadingModel) -> None:
        if self.shading_mode_loc == -1:
            return
        if shading == self.shading_mode:
            return
        self.shading_mode = shading
        self.shader_program.activate()
        GL.glUniform1i(self.shading_mode_loc, self.shading_mode.value)
        self.shader_program.deactivate()

    @staticmethod
    def _apply_color_override(
        colors: np.ndarray,
        override: tuple[float | None, float | None, float | None] | None,
    ) -> np.ndarray:
        if not override:
            return colors

        for idx, channel in enumerate(override):
            if channel is not None:
                colors[:, idx] = channel
        return colors

    def _create_texture(self, path):
        img_data, width, height = load_texture(path)
        self.texture = Texture2D()
        self.texture.add_texture(
            img_data,
            width,
            height,
        )
        GL.glActiveTexture(GL.GL_TEXTURE0)
