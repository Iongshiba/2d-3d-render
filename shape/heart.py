import numpy as np

from OpenGL import GL

from utils import *
from graphics.vertex import Vertex
from graphics.buffer import VAO
from shape.base import Shape, Part


class Heart(Shape):
    def __init__(
        self,
        sector: int = 128,
        stack: int = 64,
        scale: float = 1.0,
        color=(None, None, None),
        vertex_file=None,
        fragment_file=None,
        texture_file=None,
    ) -> None:
        super().__init__(vertex_file, fragment_file)
        if texture_file:
            self._create_texture(texture_file)

        self.sector = sector
        self.stack = stack
        self.scale = scale

        # Heart equation: (x^2 + 9/4*y^2 + z^2 - 1)^3 - x^2*z^3 - 9/200*y^2*z^3 = 0
        # We'll use spherical-like coordinates and adjust to fit the heart surface

        sides = []
        indices = []
        norms = []

        # Create a parametric surface using theta (azimuthal) and phi (polar) angles
        thetas = np.linspace(0, 2 * np.pi, sector)
        phis = np.linspace(-np.pi / 2, np.pi / 2, stack)

        for stack_idx in range(stack):
            for sector_idx in range(sector):
                theta = thetas[sector_idx]
                phi = phis[stack_idx]

                # Start with spherical coordinates and adjust to heart shape
                # Use a radius function that creates the heart shape
                r = self._heart_radius(theta, phi)

                x = r * np.cos(phi) * np.cos(theta) * scale
                y = r * np.cos(phi) * np.sin(theta) * scale
                z = r * np.sin(phi) * scale

                sides.append(
                    Vertex(
                        x,
                        y,
                        z,
                        color[0],
                        color[1],
                        color[2],
                    )
                )

                # Calculate normal by gradient of implicit function
                normal = self._calculate_normal(x, y, z)
                norms.append(normal)

                if stack_idx < stack - 1:
                    indices.extend(
                        [
                            stack_idx * sector + sector_idx,
                            (stack_idx + 1) * sector + sector_idx,
                        ]
                    )

        side_coords = vertices_to_coords(sides)
        side_colors = self._apply_color_override(vertices_to_colors(sides), color)
        indices = np.array(indices, dtype=np.int32)
        norms = np.array(norms, dtype=np.float32)

        vao = VAO()
        vao.add_vbo(
            location=0,
            data=side_coords,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_vbo(
            location=1,
            data=side_colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_vbo(
            location=2,
            data=norms,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )
        vao.add_ebo(indices)

        self.shapes.append(
            Part(
                vao,
                GL.GL_TRIANGLE_STRIP,
                side_coords.shape[0],
                indices.shape[0],
            )
        )

    def _heart_radius(self, theta, phi):
        """Calculate radius for heart shape at given spherical angles using ray-surface intersection"""
        # Direction vector from origin
        direction = np.array(
            [np.cos(phi) * np.cos(theta), np.cos(phi) * np.sin(theta), np.sin(phi)]
        )

        # Find where ray from origin intersects the heart surface
        # Use bisection method to find the intersection
        r_min = 0.1
        r_max = 2.0
        tolerance = 1e-3
        max_iterations = 20

        for _ in range(max_iterations):
            r = (r_min + r_max) / 2
            x, y, z = r * direction

            f_value = self._heart_function(x, y, z)

            if abs(f_value) < tolerance:
                return r

            # Check sign at r_min
            x_min, y_min, z_min = r_min * direction
            f_min = self._heart_function(x_min, y_min, z_min)

            if (f_value > 0) == (f_min > 0):
                r_min = r
            else:
                r_max = r

        # Return a reasonable default if convergence fails
        return (r_min + r_max) / 2

    def _calculate_normal(self, x, y, z):
        """Calculate normal vector using gradient of implicit heart equation"""
        # F(x,y,z) = (x^2 + 9/4*y^2 + z^2 - 1)^3 - x^2*z^3 - 9/200*y^2*z^3

        epsilon = 1e-4

        # Calculate partial derivatives numerically
        fx_plus = self._heart_function(x + epsilon, y, z)
        fx_minus = self._heart_function(x - epsilon, y, z)
        df_dx = (fx_plus - fx_minus) / (2 * epsilon)

        fy_plus = self._heart_function(x, y + epsilon, z)
        fy_minus = self._heart_function(x, y - epsilon, z)
        df_dy = (fy_plus - fy_minus) / (2 * epsilon)

        fz_plus = self._heart_function(x, y, z + epsilon)
        fz_minus = self._heart_function(x, y, z - epsilon)
        df_dz = (fz_plus - fz_minus) / (2 * epsilon)

        # Gradient gives the normal
        normal = np.array([df_dx, df_dy, df_dz], dtype=np.float32)

        # Normalize
        norm_length = np.linalg.norm(normal)
        if norm_length > 1e-6:
            normal = normal / norm_length
        else:
            normal = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        return normal

    def _heart_function(self, x, y, z):
        """Implicit heart equation"""
        # (x^2 + 9/4*y^2 + z^2 - 1)^3 - x^2*z^3 - 9/200*y^2*z^3
        term1 = (x**2 + 9 / 4 * y**2 + z**2 - 1) ** 3
        term2 = x**2 * z**3
        term3 = 9 / 200 * y**2 * z**3
        return term1 - term2 - term3
