import numpy as np

from OpenGL import GL

from utils.misc import load_model, load_texture
from shape.base import Shape, Part
from graphics.buffer import VAO
from config import ModelVisualizationMode


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

        # Store vertices and indices for visualization features
        self.all_vertices = []
        self.all_indices = []
        self.visualization_mode = ModelVisualizationMode.NORMAL
        self.bbox_vao = None
        self.depth_vao = None
        self.mask_vao = None

        for mesh_data in model_data:
            vao = VAO()

            # Store vertices and indices for later use
            self.all_vertices.append(mesh_data["vertices"])
            # Store the reversed indices
            indices = mesh_data["indices"]
            indices_reversed = indices.reshape(-1, 3)[:, ::-1].flatten()
            self.all_indices.append(indices_reversed)

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

            vao.add_vbo(
                location=2,
                data=mesh_data["normals"],
                ncomponents=mesh_data["normals"].shape[1],
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

            # Texture coordinates
            vao.add_vbo(
                location=3,
                data=mesh_data["tex_coords"],
                ncomponents=mesh_data["tex_coords"].shape[1],
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

            # Add the already reversed indices to VAO
            vao.add_ebo(indices_reversed)

            self.shapes.append(
                Part(
                    vao,
                    GL.GL_TRIANGLES,
                    len(mesh_data["vertices"]),
                    len(mesh_data["indices"]),
                )
            )

        # Generate visualization data
        self._generate_depth_map()
        self._generate_segmentation_mask()

        # 2D bounding box will be computed dynamically during rendering
        self.bbox_2d_vao = None
        self.current_mvp = None

    def _compute_2d_bounding_box(self, model_matrix, view_matrix, proj_matrix):
        """Compute 2D screen-space bounding box from transformed vertices."""
        if not self.all_vertices:
            return None

        # Combine all vertices
        all_verts = np.vstack(self.all_vertices)

        # Transform vertices to clip space
        mvp = proj_matrix @ view_matrix @ model_matrix

        # Add homogeneous coordinate
        vertices_homogeneous = np.hstack(
            [all_verts, np.ones((len(all_verts), 1))]
        ).astype(np.float32)

        # Transform to clip space
        clip_coords = vertices_homogeneous @ mvp.T

        # Perform perspective division to get NDC coordinates
        ndc_coords = clip_coords[:, :3] / clip_coords[:, 3:4]

        # Find 2D bounding box in NDC space (x, y in range [-1, 1])
        min_x, min_y = ndc_coords[:, 0].min(), ndc_coords[:, 1].min()
        max_x, max_y = ndc_coords[:, 0].max(), ndc_coords[:, 1].max()

        # Clamp to screen bounds
        min_x = max(min_x, -1.0)
        max_x = min(max_x, 1.0)
        min_y = max(min_y, -1.0)
        max_y = min(max_y, 1.0)

        # Create 2D rectangle corners (in NDC, z=0 for screen overlay)
        corners = np.array(
            [
                [min_x, min_y, 0.0],
                [max_x, min_y, 0.0],
                [max_x, max_y, 0.0],
                [min_x, max_y, 0.0],
            ],
            dtype=np.float32,
        )

        # Create line indices for rectangle outline
        indices = np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32)

        return corners, indices

    def _generate_depth_map(self):
        """Generate depth-based color visualization."""
        if not self.all_vertices:
            return

        # For each mesh, create depth-colored vertices
        depth_parts = []

        for i, mesh_verts in enumerate(self.all_vertices):
            # Calculate depth (Z coordinate)
            z_coords = mesh_verts[:, 2]
            z_min, z_max = z_coords.min(), z_coords.max()

            # Normalize depth to [0, 1]
            if z_max != z_min:
                normalized_depth = (z_coords - z_min) / (z_max - z_min)
            else:
                normalized_depth = np.zeros_like(z_coords)

            # Create color map (blue = near, red = far)
            depth_colors = np.zeros((len(mesh_verts), 3), dtype=np.float32)
            depth_colors[:, 0] = normalized_depth  # Red increases with depth
            depth_colors[:, 2] = 1.0 - normalized_depth  # Blue decreases with depth

            depth_parts.append(
                {
                    "vertices": mesh_verts,
                    "colors": depth_colors,
                    "indices": (
                        self.all_indices[i] if i < len(self.all_indices) else None
                    ),
                    "index_count": self.shapes[i].index_num,
                }
            )

        # Store depth parts for rendering
        self.depth_parts = depth_parts

    def _generate_segmentation_mask(self):
        """Generate segmentation mask with random colors per mesh."""
        if not self.all_vertices:
            return

        # Generate random colors for each mesh
        num_meshes = len(self.all_vertices)
        mesh_colors = np.random.rand(num_meshes, 3).astype(np.float32)

        # For each mesh, assign a uniform color
        mask_parts = []

        for i, mesh_verts in enumerate(self.all_vertices):
            # All vertices in this mesh get the same color
            mesh_color = np.tile(mesh_colors[i], (len(mesh_verts), 1))

            mask_parts.append(
                {
                    "vertices": mesh_verts,
                    "colors": mesh_color,
                    "indices": (
                        self.all_indices[i] if i < len(self.all_indices) else None
                    ),
                    "index_count": self.shapes[i].index_num,
                }
            )

        # Store mask parts for rendering
        self.mask_parts = mask_parts

    def set_visualization_mode(self, mode: ModelVisualizationMode):
        """Set the visualization mode for the model."""
        self.visualization_mode = mode

    def transform(
        self,
        project_matrix: np.ndarray,
        view_matrix: np.ndarray,
        model_matrix: np.ndarray,
    ):
        """Override to store matrices for 2D bounding box computation."""
        super().transform(project_matrix, view_matrix, model_matrix)
        # Store matrices for 2D bounding box computation
        self.stored_model_matrix = model_matrix
        self.stored_view_matrix = view_matrix
        self.stored_proj_matrix = project_matrix

    def draw(self):
        """Override draw to support different visualization modes."""
        if self.visualization_mode == ModelVisualizationMode.BOUNDING_BOX:
            super().draw()
            self._draw_2d_bounding_box()
        elif self.visualization_mode == ModelVisualizationMode.DEPTH_MAP:
            self._draw_depth_map()
        elif self.visualization_mode == ModelVisualizationMode.SEGMENTATION_MASK:
            self._draw_segmentation_mask()
        # Normal rendering
        else:
            super().draw()

    def _draw_2d_bounding_box(self):
        """Draw 2D screen-space bounding box overlay."""
        if not hasattr(self, "stored_model_matrix"):
            return

        # Compute 2D bounding box
        bbox_data = self._compute_2d_bounding_box(
            self.stored_model_matrix, self.stored_view_matrix, self.stored_proj_matrix
        )

        if bbox_data is None:
            return

        corners, indices = bbox_data

        # Create temporary VAO for 2D bbox
        vao = VAO()
        vao.add_vbo(
            location=0,
            data=corners,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        # Yellow color for visibility
        colors = np.ones((4, 3), dtype=np.float32) * [1.0, 1.0, 0.0]
        vao.add_vbo(
            location=1,
            data=colors,
            ncomponents=3,
            dtype=GL.GL_FLOAT,
            normalized=False,
            stride=0,
            offset=None,
        )

        vao.add_ebo(indices)

        self.shader_program.activate()
        GL.glUniform1i(self.use_texture_loc, 0)

        # Use identity matrices for direct NDC rendering
        identity = np.eye(4, dtype=np.float32)
        GL.glUniformMatrix4fv(self.transform_loc, 1, GL.GL_TRUE, identity)
        GL.glUniformMatrix4fv(self.camera_loc, 1, GL.GL_TRUE, identity)
        GL.glUniformMatrix4fv(self.project_loc, 1, GL.GL_TRUE, identity)

        # Disable depth test to draw on top
        GL.glDisable(GL.GL_DEPTH_TEST)

        vao.activate()
        GL.glDrawElements(GL.GL_LINES, len(indices), GL.GL_UNSIGNED_INT, None)
        vao.deactivate()

        # Re-enable depth test
        GL.glEnable(GL.GL_DEPTH_TEST)

        self.shader_program.deactivate()

    def _draw_depth_map(self):
        """Draw the depth map visualization."""
        if not hasattr(self, "depth_parts") or not self.depth_parts:
            return

        self.shader_program.activate()
        # Disable texture for depth map
        GL.glUniform1i(self.use_texture_loc, 0)

        for part in self.depth_parts:
            # Create temporary VAO for this part
            vao = VAO()
            vao.add_vbo(
                location=0,
                data=part["vertices"],
                ncomponents=3,
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )
            vao.add_vbo(
                location=1,
                data=part["colors"],
                ncomponents=3,
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

            if part["indices"] is not None:
                vao.add_ebo(part["indices"])
                vao.activate()
                GL.glDrawElements(
                    GL.GL_TRIANGLES, part["index_count"], GL.GL_UNSIGNED_INT, None
                )
            else:
                vao.activate()
                GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(part["vertices"]))

            vao.deactivate()

        self.shader_program.deactivate()

    def _draw_segmentation_mask(self):
        """Draw the segmentation mask visualization."""
        if not hasattr(self, "mask_parts") or not self.mask_parts:
            return

        self.shader_program.activate()
        # Disable texture for segmentation mask
        GL.glUniform1i(self.use_texture_loc, 0)

        for part in self.mask_parts:
            # Create temporary VAO for this part
            vao = VAO()
            vao.add_vbo(
                location=0,
                data=part["vertices"],
                ncomponents=3,
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )
            vao.add_vbo(
                location=1,
                data=part["colors"],
                ncomponents=3,
                dtype=GL.GL_FLOAT,
                normalized=False,
                stride=0,
                offset=None,
            )

            if part["indices"] is not None:
                vao.add_ebo(part["indices"])
                vao.activate()
                GL.glDrawElements(
                    GL.GL_TRIANGLES, part["index_count"], GL.GL_UNSIGNED_INT, None
                )
            else:
                vao.activate()
                GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(part["vertices"]))

            vao.deactivate()

        self.shader_program.deactivate()

    def cleanup(self):
        """Cleanup OpenGL resources including visualization VAOs."""
        super().cleanup()
        # No persistent bbox VAO to cleanup (created dynamically)
