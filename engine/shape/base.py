import numpy as np

from OpenGL import GL
from functools import reduce

from graphics.buffer import VBO, VAO, EBO
from graphics.shader import Shader, ShaderProgram
from libs.context import shader_program, vao_context


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
        self.transform_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)

        self.transform_loc = GL.glGetUniformLocation(self.shader_program.program, "transform")
        with shader_program(self.shader_program):
            GL.glUniformMatrix4fv(
                self.transform_loc, 1, GL.GL_TRUE, self.transform_matrix
            )

    def set_uniforms(self, uniforms: dict[str, float | int | tuple] | None = None):
        if not uniforms:
            return
        with shader_program(self.shader_program):
            for name, value in uniforms.items():
                loc = GL.glGetUniformLocation(self.shader_program.program, name)
                if loc == -1:
                    continue
                if isinstance(value, (tuple, list)) and len(value) == 3:
                    GL.glUniform3f(
                        loc, float(value[0]), float(value[1]), float(value[2])
                    )
                elif isinstance(value, (int,)):
                    GL.glUniform1i(loc, int(value))
                else:
                    try:
                        GL.glUniform1f(loc, float(value))
                    except Exception:
                        pass

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

    def transform(self, matrix):
        # Accept a single matrix/function or a list of them.
        items = matrix
        if not isinstance(items, (list, tuple)):
            items = [items]

        # Update an animation parameter if desired
        if self.alpha <= -10 or self.alpha >= 30:
            self.delta *= -1
        self.alpha += self.delta

        # Multiply in the provided order: e.g., [projection, view, model]
        # With gl_Position = transform * vec4(pos,1), this applies model first, then view, then projection.
        final = reduce(np.dot, items)
        with shader_program(self.shader_program):
            GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, final)

    def scale(self, factor=1):
        transform_matrix = np.copy(self.transform_matrix)
        transform_matrix[0, 0] = np.float32(factor)
        transform_matrix[1, 1] = np.float32(factor)
        transform_matrix[2, 2] = np.float32(factor)
        return transform_matrix

    def translate(self):
        transform_matrix = np.copy(self.transform_matrix)
        transform_matrix[2, 3] = self.alpha
        # transform_matrix[1, 3] = self.alpha
        return transform_matrix
    
    def rotate(self, axis='x'):
        transform_matrix = np.copy(self.transform_matrix)
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

    def project(self, fov=90.0, aspect_ratio=1.0, near=0.1, far=100.0):
        fov_rad = np.radians(fov)
        f = np.float32(1.0 / np.tan(fov_rad / 2.0))
        
        # Standard right-handed perspective matrix (row-major here; we pass transpose=True to OpenGL)
        # x' = (f/aspect) * x, y' = f * y
        # z' = (far+near)/(near-far) * z + (2*far*near)/(near-far)
        # w' = -z
        proj = np.zeros((4, 4), dtype=np.float32)
        proj[0, 0] = f / np.float32(aspect_ratio)
        proj[1, 1] = f
        proj[2, 2] = (far + near) / (near - far)
        proj[2, 3] = (2.0 * far * near) / (near - far)
        proj[3, 2] = -1.0
        # proj[3, 3] stays 0
        return proj
        
    # def draw(self):
    #     self.shader_program.activate()
    #     self.vao.activate()

    #     if self.indices is not None:
    #         gl_type = (
    #             GL.GL_UNSIGNED_INT
    #             if self.indices.dtype == np.uint32
    #             else GL.GL_UNSIGNED_SHORT
    #         )
    #         GL.glDrawElements(GL.GL_TRIANGLES, int(self.indices.size), gl_type, None)
    #     else:
    #         GL.glDrawArrays(GL.GL_TRIANGLES, 0, int(self.vertex_count))

    #     self.vao.deactivate()
    #     self.shader_program.deactivate()
