import numpy as np

from OpenGL import GL

from utils.misc import load_model, load_texture
from shape.base import Shape, Part
from graphics.buffer import VAO


class Model(Shape):
    def __init__(
        self,
        model_path,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ):
        super().__init__(vertex_file, fragment_file)

        if texture_file:
            self._create_texture(texture_file)

        model_data = load_model(model_path)

        for mesh_data in model_data:
            vao = VAO()

            # Vertex positions
            vao.add_vbo(
                location=0,
                data=mesh_data["vertices"],
                ncomponents=mesh_data["vertices"].shape[1],
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

            # Texture coordinates
            if mesh_data["tex_coords"] is not None:
                vao.add_vbo(
                    location=2,
                    data=mesh_data["tex_coords"],
                    ncomponents=mesh_data["tex_coords"].shape[1],
                    dtype=GL.GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=None,
                )

            # Indices
            vao.add_ebo(mesh_data["indices"])

            self.shapes.append(
                Part(
                    vao,
                    GL.GL_TRIANGLES,
                    len(mesh_data["vertices"]),
                    len(mesh_data["indices"]),
                )
            )
