import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Equation(Shape):
    def __init__(
        self,
        expression,
        mesh_size,
        mesh_density,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ):
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.expression = expression
        self.mesh_size = mesh_size
        self.mesh_density = mesh_density

        func = make_numpy_func(expression)
        x_ = np.linspace(-mesh_size / 2, mesh_size / 2, mesh_density)
        y_ = np.linspace(-mesh_size / 2, mesh_size / 2, mesh_density)
        X, Y = np.meshgrid(x_, y_, indexing="xy")
        Z = func(X, Y)
        Z_min = np.min(Z)
        Z_max = np.max(Z)
        Z_normalized = (Z - Z_min) / (Z_max - Z_min) * 10
        Z_flat = Z_normalized.flatten() / 10

        # Norm vectors
        x_step = x_[1] - x_[0]
        y_step = y_[1] - y_[0]
        dZ_dx = np.zeros_like(Z)
        dZ_dy = np.zeros_like(Z)
        # central
        dZ_dx[:, 1:-1] = (Z[:, 2:] - Z[:, :-2]) / (2 * x_step)
        dZ_dy[1:-1, :] = (Z[2:, :] - Z[:-2, :]) / (2 * y_step)
        # borders
        dZ_dx[:, 0] = (Z[:, 1] - Z[:, 0]) / x_step
        dZ_dx[:, -1] = (Z[:, -1] - Z[:, -2]) / x_step
        dZ_dy[0, :] = (Z[1, :] - Z[0, :]) / y_step
        dZ_dy[-1, :] = (Z[-1, :] - Z[-2, :]) / y_step
        # norm
        norms = np.zeros((mesh_density * mesh_density, 3), dtype=np.float32)
        norms_ = np.zeros((mesh_density * mesh_density, 3), dtype=np.float32)
        norms[:, 0] = -dZ_dx.flatten()
        norms[:, 1] = -dZ_dy.flatten()
        norms[:, 2] = 1
        norms_[:, 0] = dZ_dx.flatten()
        norms_[:, 1] = dZ_dy.flatten()
        norms_[:, 2] = 1
        # norms = np.concat([norms, norms_])
        norms = norms / np.linalg.norm(norms, axis=1, keepdims=True)

        # Create pastel heatmap colors: blue (low) -> cyan -> green -> yellow -> red (high)
        colors = np.zeros((len(Z_flat), 3), dtype=np.float32)
        pastel_factor = 0.6  # Reduces color intensity
        pastel_base = 0.4  # Adds brightness to all channels

        for idx, z_norm in enumerate(Z_flat):
            if z_norm < 0.25:
                # Blue to Cyan
                t = z_norm / 0.25
                color = [0.0, t, 1.0]
            elif z_norm < 0.5:
                # Cyan to Green
                t = (z_norm - 0.25) / 0.25
                color = [0.0, 1.0, 1.0 - t]
            elif z_norm < 0.75:
                # Green to Yellow
                t = (z_norm - 0.5) / 0.25
                color = [t, 1.0, 0.0]
            else:
                # Yellow to Red
                t = (z_norm - 0.75) / 0.25
                color = [1.0, 1.0 - t, 0.0]

            # Apply pastel effect
            colors[idx] = [pastel_base + c * pastel_factor for c in color]

        vertices = [
            Vertex(x, y, z)
            for x, y, z in zip(X.flatten(), Y.flatten(), Z_normalized.flatten())
        ]

        coords = vertices_to_coords(vertices)
        # colors = vertices_to_colors(vertices)

        indices = []
        indices_ = []
        for i in range(mesh_density - 1):
            strips = []
            strips_ = []
            for j in range(mesh_density):
                strips.extend(
                    [
                        i * mesh_density + j,
                        (i + 1) * mesh_density + j,
                    ]
                )
                strips_.extend(
                    [
                        (i + 1) * mesh_density + j,
                        i * mesh_density + j,
                    ]
                )
            # Remove redundant connection between odd-even strip
            # Only even-odd strip is allowed
            if i < mesh_density - 2:
                strips.extend(
                    [
                        (i + 1) * mesh_density + (mesh_density - 1),
                        (i + 1) * mesh_density,
                    ]
                )
                strips_.extend(
                    [
                        i * mesh_density + (mesh_density - 1),
                        (i + 2) * mesh_density,
                    ]
                )
            indices.extend(strips)
            indices_.extend(strips_)

        # indices.extend([indices[-1], indices_[0]])
        # indices.extend(indices_)
        indices = np.array(indices, dtype=np.int32)
        # print(indices.shape)
        # print(norms.shape)

        vao = VAO()
        vao.add_vbo(
            location=0,
            data=coords,
            ncomponents=coords.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_vbo(
            location=1,
            data=colors,
            ncomponents=colors.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_vbo(
            location=2,
            data=norms,
            ncomponents=norms.shape[1],
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        if texture_file:
            # Generate UV texture coordinates based on X, Y mesh positions
            # Map the mesh coordinates to [0, 1] range for texture sampling
            texcoords = np.zeros((len(vertices), 2), dtype=np.float32)

            # Normalize X and Y coordinates to [0, 1] range
            X_flat = X.flatten()
            Y_flat = Y.flatten()

            X_min, X_max = X_flat.min(), X_flat.max()
            Y_min, Y_max = Y_flat.min(), Y_flat.max()

            # Handle edge case where min == max
            X_range = X_max - X_min if X_max != X_min else 1.0
            Y_range = Y_max - Y_min if Y_max != Y_min else 1.0

            u = (X_flat - X_min) / X_range
            v = (Y_flat - Y_min) / Y_range

            texcoords[:, 0] = u
            texcoords[:, 1] = v

            vao.add_vbo(
                location=3,
                data=texcoords,
                ncomponents=2,
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

        vao.add_ebo(indices)

        self.shapes.extend(
            [Part(vao, GL.GL_TRIANGLE_STRIP, len(vertices), len(indices))]
        )

        self.surface = (X, Y, Z_normalized)
        self.normals = norms[: (mesh_density * mesh_density)].reshape(
            (mesh_density, mesh_density, 3)
        )
        self.func = func
        self.Z_max = Z_max
        self.Z_min = Z_min
