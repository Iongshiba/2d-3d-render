import numpy as np

from OpenGL import GL
from functools import reduce
from typing import Callable, Iterable

from graphics.buffer import VAO, EBO
from graphics.shader import Shader, ShaderProgram
from utils import shader_program, vao_context


class ShapeCandidate:
    def __init__(
        self,
        vao_id: int,
        draw_mode: int,
        attributes: dict[int : np.ndarray],
        indices: np.ndarray | None = None,
    ):
        self.vao_id = vao_id
        self.draw_mode = draw_mode
        self.attributes = attributes
        self.indices = indices
        self.vertex_count = len(attributes[0])


# fmt: off
class Shape:
    def __init__(self, vertex_file: str, fragment_file: str):
        # Shaders
        vertex_shader = Shader(vertex_file)
        fragment_shader = Shader(fragment_file)
        self.shader_program = ShaderProgram()
        self.shader_program.add_shader(vertex_shader)
        self.shader_program.add_shader(fragment_shader)
        self.shader_program.build()

        # Geometry containers
        self.shape_candidates = []
        self.vaos: dict[int, VAO] = {}
        self.ebos: dict[int, EBO] = {}
        self.indices: np.ndarray | None = None
        self.vertex_count: int = 0

        self.identity = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )

        self.transform_loc = GL.glGetUniformLocation(
            self.shader_program.program, "transform"
        )
        self.camera_loc = GL.glGetUniformLocation(
            self.shader_program.program, "camera"
        )
        self.project_loc = GL.glGetUniformLocation(
            self.shader_program.program, "project"
        )

        with shader_program(self.shader_program):
            GL.glUniformMatrix4fv(
                self.transform_loc, 1, GL.GL_TRUE, self.identity
            )
            GL.glUniformMatrix4fv(
                self.camera_loc, 1, GL.GL_TRUE, self.identity
            )
            GL.glUniformMatrix4fv(
                self.project_loc, 1, GL.GL_TRUE, self.identity
            )

    # def setup_buffers(self):
    #     # Determine vertex count from the first attribute
    #     if not self.shape_candidates:
    #         raise ValueError("No shape candidate provided")

    #     for shape in self.shape_candidates:
    #         vao = shape.vao_id              # vao id of the current shape candidate

    #         self.vaos[vao] = VAO()          # Init the vao the current shapea candidate

    #         # Create and attach VBOs
    #         for location, data in shape.attributes.items():
    #             ncomponents = int(data.shape[1])                    # x,y,z so ncomponents = 3
    #             vbo = VBO(location, data, ncomponents=ncomponents)
    #             self.vaos[vao].add_vbo(vbo) 
    #             self.vbos[location] = vbo

    #         # Create and attach EBO if indices provided
    #         if shape.indices is not None:
    #             ebo = EBO(shape.indices)
    #             self.ebos[vao] = ebo
    #             self.vaos[vao].add_ebo(ebo)

    def draw(self):
        for candidate in self.shape_candidates:
            vao = self.vaos[candidate.vao_id]
            with shader_program(self.shader_program), vao_context(vao):
                if candidate.indices is not None:
                    GL.glDrawElements(
                        candidate.draw_mode, int(candidate.indices.size), GL.GL_UNSIGNED_INT, None
                    )
                else:
                    GL.glDrawArrays(candidate.draw_mode, 0, int(candidate.vertex_count))

    def transform(self, project_matrix, view_matrix, model_matrix):
        with shader_program(self.shader_program):
            if self.project_loc != -1:
                GL.glUniformMatrix4fv(
                    self.project_loc, 1, GL.GL_TRUE, project_matrix
                )
            if self.camera_loc != -1:
                GL.glUniformMatrix4fv(
                    self.camera_loc, 1, GL.GL_TRUE, view_matrix
                )
            if self.transform_loc != -1:
                GL.glUniformMatrix4fv(
                    self.transform_loc, 1, GL.GL_TRUE, model_matrix
                )
