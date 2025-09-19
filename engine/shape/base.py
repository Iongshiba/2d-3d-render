import numpy as np

from OpenGL import GL

from libs.buffer import VBO, VAO, EBO
from libs.shader import Shader, ShaderProgram

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
        self.vao = VAO()
        self.vbos: dict[int, VBO] = {}
        self.ebo: EBO | None = None
        self.indices: np.ndarray | None = None
        self.vertex_count: int = 0

        self.delta = 0.005
        self.alpha = 1.0
        self.transform_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)


        self.transform_loc = GL.glGetUniformLocation(self.shader_program.program, "transform")
        self.shader_program.activate()
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, self.transform_matrix)
        self.shader_program.deactivate()

    def setup_buffers(
        self, attributes: dict[int, np.ndarray], indices: np.ndarray | None = None
    ):
        """
        attributes: mapping of attribute location -> numpy array of shape (N, C)
        indices: optional numpy array of dtype uint16/uint32
        """
        # Determine vertex count from the first attribute
        if not attributes:
            raise ValueError("No vertex attributes provided")

        first_attr = next(iter(attributes.values()))
        if first_attr.ndim != 2:
            raise ValueError("Attribute arrays must be 2D: (N, C)")
        self.vertex_count = int(first_attr.shape[0])

        # Create and attach VBOs
        for location, data in attributes.items():
            if data.shape[0] != self.vertex_count:
                raise ValueError("All attribute arrays must have the same vertex count")
            ncomponents = int(data.shape[1])
            vbo = VBO(location, data, ncomponents=ncomponents)
            self.vao.add_vbo(vbo)
            self.vbos[location] = vbo

        # Create and attach EBO if indices provided
        if indices is not None:
            if indices.dtype not in (np.uint16, np.uint32):
                raise ValueError("Index array must have dtype uint16 or uint32")
            self.indices = indices
            self.ebo = EBO(indices)
            self.vao.add_ebo(self.ebo)

    def transform(self, fn, *args):
        if self.alpha <= -1 or self.alpha >= 1:
            self.delta *= -1
        self.alpha += self.delta
        fn(*args)

    def scale(self, factor=1):
        transform_matrix = np.copy(self.transform_matrix)
        transform_matrix[0, 0] = np.float32(factor)
        transform_matrix[1, 1] = np.float32(factor)
        transform_matrix[2, 2] = np.float32(factor)
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, transform_matrix)

    def translate(self):
        transform_matrix = np.copy(self.transform_matrix)
        transform_matrix[0, 3] = self.alpha
        transform_matrix[1, 3] = self.alpha
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, transform_matrix)
    
    def rotate(self, axis='x'):
        transform_matrix = np.copy(self.transform_matrix)
        rotation = np.array([
            [np.cos(self.alpha), -np.sin(self.alpha)],
            [np.sin(self.alpha), np.cos(self.alpha)],
        ], dtype=np.float32)
        anchor = (0, 0)
        if axis == 'x':
            anchor = (0, 0)
        elif axis == 'y':
            anchor = (1, 1)
        elif axis == 'z':
            anchor = (2, 2)
        transform_matrix[anchor[0] : anchor[0] + 2, anchor[1] : anchor[1] + 2] = rotation
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, transform_matrix)
        
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
