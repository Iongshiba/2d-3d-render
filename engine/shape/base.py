import numpy as np

from OpenGL import GL
from functools import reduce
from typing import Callable, Iterable, Sequence

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

        self.delta = 0.00005
        self.alpha = 1.0
        self.identity = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)
        self.transform_matrix = np.copy(self.identity)

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

    def aspect_ratio(self, app) -> float:
        """Safely retrieve the app's aspect ratio (defaults to 1.0)."""

        if app and hasattr(app, "get_aspect_ratio"):
            return float(app.get_aspect_ratio())
        return 1.0

    # TODO create a transform class that accept transform
    # maybe implement visitor pattern for this transform since camera also is a transform
    #
    
    def transform(self, matrix):
        # Accept a single matrix/function or a list of them.
        items = matrix
        if not isinstance(items, (list, tuple)):
            items = [items]

        # Update an animation parameter if desired
        if self.alpha <= -5 or self.alpha >= 5:
            self.delta *= -1
        self.alpha += self.delta

        # Multiply in the provided order: e.g., [projection, view, model]
        # With gl_Position = transform * vec4(pos,1), this applies model first, then view, then projection.
        final = reduce(np.dot, items)
        with shader_program(self.shader_program):
            GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, final)

    def scale(self, factor=1):
        transform_matrix = np.copy(self.identity)
        transform_matrix[0, 0] = np.float32(factor)
        transform_matrix[1, 1] = np.float32(factor)
        transform_matrix[2, 2] = np.float32(factor)
        return transform_matrix

    def translate(self):
        transform_matrix = np.copy(self.identity)
        transform_matrix[2, 3] = self.alpha
        # transform_matrix[1, 3] = self.alpha
        return transform_matrix
    
    def rotate(self, axis='x'):
        transform_matrix = np.copy(self.identity)
        rotation = np.array([
            [np.cos(self.alpha), -np.sin(self.alpha)],
            [np.sin(self.alpha), np.cos(self.alpha)],
        ], dtype=np.float32)
        if axis == 'x':
            transform_matrix[1:3, 1:3] = rotation
        elif axis == 'y':
            transform_matrix[0, 0] = rotation[0][0]
            transform_matrix[0, 2] = rotation[0][1]
            transform_matrix[2, 0] = rotation[1][0]
            transform_matrix[2, 2] = rotation[1][1]
        elif axis == 'z':
            transform_matrix[0:2, 0:2] = rotation
        return transform_matrix

    def set_camera_matrices(
        self,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
    ) -> None:
        with shader_program(self.shader_program):
            if self.camera_loc != -1:
                GL.glUniformMatrix4fv(
                    self.camera_loc, 1, GL.GL_TRUE, view_matrix
                )
            if self.project_loc != -1:
                GL.glUniformMatrix4fv(
                    self.project_loc, 1, GL.GL_TRUE, projection_matrix
                )
