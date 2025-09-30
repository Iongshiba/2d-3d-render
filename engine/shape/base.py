import numpy as np

from OpenGL import GL
from functools import reduce
from typing import Callable, Iterable

from graphics.buffer import VBO, VAO, EBO
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
    """
    Base class for drawable shapes.
    Responsibilities:
    - Owns a VAO and optional VBOs/EBO
    - Owns a shader program built from provided vertex/fragment files
    - Provides setup from numpy arrays and a default draw implementation
    """

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
        self.vbos: dict[int, VBO] = {}
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

    def setup_buffers(self):
        """
        attributes: mapping of attribute location -> numpy array of shape (N, C)
        indices: optional numpy array of dtype uint16/uint32
        """
        # Determine vertex count from the first attribute
        if not self.shape_candidates:
            raise ValueError("No shape candidate provided")

        for shape in self.shape_candidates:
            vao = shape.vao_id

            self.vaos[vao] = VAO()

            # Create and attach VBOs
            for location, data in shape.attributes.items():
                ncomponents = int(data.shape[1])
                vbo = VBO(location, data, ncomponents=ncomponents)
                self.vaos[vao].add_vbo(vbo)
                self.vbos[location] = vbo

            # Create and attach EBO if indices provided
            if shape.indices is not None:
                ebo = EBO(shape.indices)
                self.ebos[vao] = ebo
                self.vaos[vao].add_ebo(ebo)

    def _draw_candidates(
        self,
        app,
        handler: Callable[["ShapeCandidate", object | None], None],
    ) -> None:
        """Iterate through shape candidates with shader and VAO bound."""

        for candidate in self.shape_candidates:
            vao = self.vaos[candidate.vao_id]
            with shader_program(self.shader_program), vao_context(vao):
                handler(candidate, app)

    def _draw_shape(self, candidate: "ShapeCandidate") -> None:
        """Issue the appropriate draw call for a candidate."""

        if candidate.indices is not None:
            gl_type = (
                GL.GL_UNSIGNED_INT
                if candidate.indices.dtype == np.uint32
                else GL.GL_UNSIGNED_SHORT
            )
            GL.glDrawElements(
                candidate.draw_mode, int(candidate.indices.size), gl_type, None
            )
        else:
            GL.glDrawArrays(candidate.draw_mode, 0, int(candidate.vertex_count))

    def transform(self, matrices: Iterable[np.ndarray]) -> None:
        """Upload ordered projection, view, and model matrices."""

        if not isinstance(matrices, (list, tuple)):
            matrices = [matrices]

        prepared = [np.array(m, dtype=np.float32) for m in matrices]

        project_matrix = self.identity
        view_matrix = self.identity
        model_matrix = self.identity

        if prepared:
            project_matrix = prepared[0]
        if len(prepared) >= 2:
            view_matrix = prepared[1]
        if len(prepared) >= 3:
            model_parts = prepared[2:]
            if len(model_parts) == 1:
                model_matrix = model_parts[0]
            else:
                model_matrix = reduce(np.dot, model_parts)

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

    def draw(self, app=None):
        def render(candidate, _):
            self._draw_shape(candidate)

        self._draw_candidates(app, render)
