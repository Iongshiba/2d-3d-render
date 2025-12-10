import numpy as np

from pathlib import Path
from OpenGL import GL

from utils import *
from config import (
    _SHAPE_FRAGMENT_PATH,
    _SHAPE_VERTEX_PATH,
    _GOURAUD_VERTEX_PATH,
    _GOURAUD_FRAGMENT_PATH,
    _NORMAL_VERTEX_PATH,
    _NORMAL_FRAGMENT_PATH,
    ShadingModel,
)
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
        # Ignore passed parameters - we now create all 3 shader programs
        # Create three separate shader programs for each shading technique

        # Normal shading program
        self.normal_program = ShaderProgram()
        self.normal_program.add_shader(Shader(_NORMAL_VERTEX_PATH))
        self.normal_program.add_shader(Shader(_NORMAL_FRAGMENT_PATH))
        self.normal_program.build()

        # Phong shading program
        self.phong_program = ShaderProgram()
        self.phong_program.add_shader(Shader(_SHAPE_VERTEX_PATH))
        self.phong_program.add_shader(Shader(_SHAPE_FRAGMENT_PATH))
        self.phong_program.build()

        # Gouraud shading program
        self.gouraud_program = ShaderProgram()
        self.gouraud_program.add_shader(Shader(_GOURAUD_VERTEX_PATH))
        self.gouraud_program.add_shader(Shader(_GOURAUD_FRAGMENT_PATH))
        self.gouraud_program.build()

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
        self.texture_enabled = False
        self.shading_mode = ShadingModel.PHONG

        # Get uniform locations for all three programs
        self._init_uniform_locations()

        # Initialize default uniform values for all programs
        self._init_uniform_defaults()

    def _init_uniform_locations(self):
        """Get uniform locations for all shader programs."""
        # Common uniforms (present in all shaders)
        self.transform_locs = {}
        self.camera_locs = {}
        self.project_locs = {}
        self.use_texture_locs = {}
        self.texture_data_locs = {}

        # Lighting uniforms (not in normal shader)
        self.I_lights_locs = {}
        self.K_materials_locs = {}
        self.shininess_locs = {}
        self.light_coord_locs = {}

        for mode, program in [
            (ShadingModel.NORMAL, self.normal_program),
            (ShadingModel.PHONG, self.phong_program),
            (ShadingModel.GOURAUD, self.gouraud_program),
        ]:
            self.transform_locs[mode] = GL.glGetUniformLocation(
                program.program, "transform"
            )
            self.camera_locs[mode] = GL.glGetUniformLocation(program.program, "camera")
            self.project_locs[mode] = GL.glGetUniformLocation(
                program.program, "project"
            )
            self.use_texture_locs[mode] = GL.glGetUniformLocation(
                program.program, "use_texture"
            )
            self.texture_data_locs[mode] = GL.glGetUniformLocation(
                program.program, "textureData"
            )

            # Lighting uniforms (only for Phong and Gouraud)
            if mode != ShadingModel.NORMAL:
                self.I_lights_locs[mode] = GL.glGetUniformLocation(
                    program.program, "I_lights"
                )
                self.K_materials_locs[mode] = GL.glGetUniformLocation(
                    program.program, "K_materials"
                )
                self.shininess_locs[mode] = GL.glGetUniformLocation(
                    program.program, "shininess"
                )
                self.light_coord_locs[mode] = GL.glGetUniformLocation(
                    program.program, "lightCoord"
                )

    def _init_uniform_defaults(self):
        """Initialize default uniform values for all shader programs."""
        for mode, program in [
            (ShadingModel.NORMAL, self.normal_program),
            (ShadingModel.PHONG, self.phong_program),
            (ShadingModel.GOURAUD, self.gouraud_program),
        ]:
            program.activate()

            # Common uniforms
            GL.glUniformMatrix4fv(
                self.transform_locs[mode], 1, GL.GL_TRUE, self.identity
            )
            GL.glUniformMatrix4fv(self.camera_locs[mode], 1, GL.GL_TRUE, self.identity)
            GL.glUniformMatrix4fv(self.project_locs[mode], 1, GL.GL_TRUE, self.identity)
            GL.glUniform1i(self.use_texture_locs[mode], False)
            GL.glUniform1i(self.texture_data_locs[mode], 0)

            # Lighting uniforms (only for Phong and Gouraud)
            if mode != ShadingModel.NORMAL:
                if self.shininess_locs[mode] != -1:
                    GL.glUniform1f(self.shininess_locs[mode], 32.0)

                if self.I_lights_locs[mode] != -1:
                    I = np.zeros((3, 3), dtype=np.float32)
                    I[:, 0] = np.array([1.0, 1.0, 1.0], dtype=np.float32)
                    I[:, 1] = np.array([1.0, 1.0, 1.0], dtype=np.float32)
                    I[:, 2] = np.array([1.0, 1.0, 1.0], dtype=np.float32)
                    GL.glUniformMatrix3fv(self.I_lights_locs[mode], 1, GL.GL_TRUE, I)

                if self.K_materials_locs[mode] != -1:
                    K = np.zeros((3, 3), dtype=np.float32)
                    K[:, 0] = np.array([0.7, 0.7, 0.7], dtype=np.float32)  # diffuse
                    K[:, 1] = np.array([0.3, 0.3, 0.3], dtype=np.float32)  # specular
                    K[:, 2] = np.array([10.0, 10.0, 10.0], dtype=np.float32)  # ambient
                    GL.glUniformMatrix3fv(self.K_materials_locs[mode], 1, GL.GL_TRUE, K)

            program.deactivate()

    def _get_active_program(self) -> ShaderProgram:
        """Get the currently active shader program based on shading mode."""
        if self.shading_mode == ShadingModel.NORMAL:
            return self.normal_program
        elif self.shading_mode == ShadingModel.GOURAUD:
            return self.gouraud_program
        else:  # PHONG
            return self.phong_program

    def draw(self):
        program = self._get_active_program()
        mode = self.shading_mode

        program.activate()
        # Set use_texture based on whether texture exists
        GL.glUniform1i(self.use_texture_locs[mode], 1 if self.texture_enabled else 0)
        for shape in self.shapes:
            vao = shape.vao
            vao.activate()
            if self.texture and self.texture_enabled:
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
            if self.texture and self.texture_enabled:
                self.texture.deactivate()
            vao.deactivate()
        program.deactivate()

    def transform(
        self,
        project_matrix: np.ndarray,
        view_matrix: np.ndarray,
        model_matrix: np.ndarray,
    ):
        program = self._get_active_program()
        mode = self.shading_mode

        program.activate()
        GL.glUniformMatrix4fv(self.project_locs[mode], 1, GL.GL_TRUE, project_matrix)
        GL.glUniformMatrix4fv(self.camera_locs[mode], 1, GL.GL_TRUE, view_matrix)
        GL.glUniformMatrix4fv(self.transform_locs[mode], 1, GL.GL_TRUE, model_matrix)
        program.deactivate()

    def lighting(
        self,
        light_color: np.ndarray,
        light_position: np.ndarray,
        camera_position: np.ndarray,
    ):
        # Skip lighting for NORMAL mode
        if self.shading_mode == ShadingModel.NORMAL:
            return

        program = self._get_active_program()
        mode = self.shading_mode

        program.activate()

        # Columns correspond to [diffuse, specular, unused].
        if self.I_lights_locs[mode] != -1:
            I = np.zeros((3, 3), dtype=np.float32)
            I[:, 0] = np.array(light_color, dtype=np.float32)
            I[:, 1] = np.array(light_color, dtype=np.float32)
            I[:, 2] = np.array(light_color, dtype=np.float32)
            GL.glUniformMatrix3fv(self.I_lights_locs[mode], 1, GL.GL_TRUE, I)

        # material coefficients modify this method in the specific shape class.
        if self.K_materials_locs[mode] != -1:
            K = np.zeros((3, 3), dtype=np.float32)
            # diffuse
            K[:, 0] = np.array([1.0, 1.0, 1.0], dtype=np.float32)
            # specular
            K[:, 1] = np.array([0.2, 0.2, 0.2], dtype=np.float32)
            # ambient
            K[:, 2] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            GL.glUniformMatrix3fv(self.K_materials_locs[mode], 1, GL.GL_TRUE, K)

        if self.shininess_locs[mode] != -1:
            GL.glUniform1f(self.shininess_locs[mode], 32.0)

        # light position should be provided in eye-space
        if self.light_coord_locs[mode] != -1:
            GL.glUniform3fv(self.light_coord_locs[mode], 1, light_position)
        program.deactivate()

    def set_shading_mode(self, shading: ShadingModel) -> None:
        """Switch to a different shading mode by changing the active shader program."""
        if shading == self.shading_mode:
            return
        self.shading_mode = shading

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

    def set_texture_enabled(self, enabled: bool) -> None:
        """Enable or disable texture mapping for this shape."""
        self.texture_enabled = enabled

    def cleanup(self):
        """Cleanup OpenGL resources used by this shape."""
        try:
            # Clean up all VAOs
            for part in self.shapes:
                if hasattr(part.vao, "cleanup"):
                    part.vao.cleanup()

            # Clean up texture if exists
            if self.texture and hasattr(self.texture, "cleanup"):
                self.texture.cleanup()

            # Clean up all three shader programs
            if hasattr(self.normal_program, "cleanup"):
                self.normal_program.cleanup()
            if hasattr(self.phong_program, "cleanup"):
                self.phong_program.cleanup()
            if hasattr(self.gouraud_program, "cleanup"):
                self.gouraud_program.cleanup()
        except Exception:
            pass  # Silently ignore cleanup errors
