# import pyassimp
import sympy as sp
import numpy as np
import pyassimp
from OpenGL import GL
from PIL import Image
from plyfile import PlyData


def make_numpy_func(expr, vars=("x", "y")):
    # Define symbols for all variable names
    symbols = sp.symbols(vars)
    # Parse the expression safely
    sym_expr = sp.sympify(expr)
    # Convert symbolic expression to NumPy function
    f = sp.lambdify(symbols, sym_expr, modules=["numpy"])
    return f


def make_numpy_deri(expr, vars=("x", "y")):
    symbols = sp.symbols(vars)
    sym_expr = sp.sympify(expr)
    dx = sp.diff(sym_expr, symbols[0])
    dy = sp.diff(sym_expr, symbols[1])
    fdx = sp.lambdify(symbols, dx, modules=["numpy"])
    fdy = sp.lambdify(symbols, dy, modules=["numpy"])
    return fdx, fdy


def load_texture(path):
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
    img_data = img.tobytes()

    return img_data, *(img.size)


def vertices_to_coords(vertices):
    return np.array([o.vertex.flatten() for o in vertices], dtype=np.float32)


def vertices_to_colors(vertices):
    return np.array([o.color.flatten() for o in vertices], dtype=np.float32)


def generate_gradient_colors(vertices, gradient_mode, start_color, end_color):
    """
    Generate gradient colors for vertices based on gradient mode.

    Args:
        vertices: List of Vertex objects or numpy array of coordinates
        gradient_mode: GradientMode enum value
        start_color: tuple (r, g, b) for start color (0-1 range)
        end_color: tuple (r, g, b) for end color (0-1 range)

    Returns:
        numpy array of colors (n_vertices, 3)
    """
    from config import GradientMode

    # Extract coordinates
    if hasattr(vertices[0], "vertex"):
        coords = np.array([v.vertex for v in vertices], dtype=np.float32)
    else:
        coords = np.array(vertices, dtype=np.float32)

    n_vertices = len(coords)
    colors = np.zeros((n_vertices, 3), dtype=np.float32)

    start_color = np.array(start_color, dtype=np.float32)
    end_color = np.array(end_color, dtype=np.float32)

    if gradient_mode == GradientMode.NONE or gradient_mode is None:
        # Return uniform color (start_color)
        colors[:] = start_color

    elif gradient_mode == GradientMode.LINEAR_X:
        # Gradient along X axis
        x_coords = coords[:, 0]
        x_min, x_max = x_coords.min(), x_coords.max()
        if x_max != x_min:
            t = (x_coords - x_min) / (x_max - x_min)
        else:
            t = np.zeros_like(x_coords)
        colors = start_color + np.outer(t, (end_color - start_color))

    elif gradient_mode == GradientMode.LINEAR_Y:
        # Gradient along Y axis
        y_coords = coords[:, 1]
        y_min, y_max = y_coords.min(), y_coords.max()
        if y_max != y_min:
            t = (y_coords - y_min) / (y_max - y_min)
        else:
            t = np.zeros_like(y_coords)
        colors = start_color + np.outer(t, (end_color - start_color))

    elif gradient_mode == GradientMode.LINEAR_Z:
        # Gradient along Z axis
        z_coords = coords[:, 2]
        z_min, z_max = z_coords.min(), z_coords.max()
        if z_max != z_min:
            t = (z_coords - z_min) / (z_max - z_min)
        else:
            t = np.zeros_like(z_coords)
        colors = start_color + np.outer(t, (end_color - start_color))

    elif gradient_mode == GradientMode.RADIAL:
        # Radial gradient from center
        center = coords.mean(axis=0)
        distances = np.linalg.norm(coords - center, axis=1)
        d_min, d_max = distances.min(), distances.max()
        if d_max != d_min:
            t = (distances - d_min) / (d_max - d_min)
        else:
            t = np.zeros_like(distances)
        colors = start_color + np.outer(t, (end_color - start_color))

    elif gradient_mode == GradientMode.DIAGONAL:
        # Diagonal gradient (X + Y + Z)
        diagonal = coords[:, 0] + coords[:, 1] + coords[:, 2]
        d_min, d_max = diagonal.min(), diagonal.max()
        if d_max != d_min:
            t = (diagonal - d_min) / (d_max - d_min)
        else:
            t = np.zeros_like(diagonal)
        colors = start_color + np.outer(t, (end_color - start_color))

    elif gradient_mode == GradientMode.RAINBOW:
        # Rainbow gradient (hue cycle)
        # Use Y coordinate for rainbow
        y_coords = coords[:, 1]
        y_min, y_max = y_coords.min(), y_coords.max()
        if y_max != y_min:
            t = (y_coords - y_min) / (y_max - y_min)
        else:
            t = np.zeros_like(y_coords)

        # Convert HSV to RGB (H varies, S=1, V=1)
        for i, hue in enumerate(t):
            h = hue * 6.0  # Hue 0-6
            c = 1.0
            x = c * (1.0 - abs((h % 2) - 1.0))
            m = 0.0

            if h < 1:
                r, g, b = c, x, 0
            elif h < 2:
                r, g, b = x, c, 0
            elif h < 3:
                r, g, b = 0, c, x
            elif h < 4:
                r, g, b = 0, x, c
            elif h < 5:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x

            colors[i] = [r + m, g + m, b + m]

    return colors


def load_ply(path):
    """Load a PLY file and return mesh data in the same format as pyassimp."""
    meshes = []
    ply_data = PlyData.read(path)

    # Extract vertex data
    vertex_data = ply_data["vertex"]
    vertices = np.column_stack(
        [vertex_data["x"], vertex_data["y"], vertex_data["z"]]
    ).astype(np.float32)

    # Extract normals (if available)
    if "nx" in vertex_data and "ny" in vertex_data and "nz" in vertex_data:
        normals = np.column_stack(
            [vertex_data["nx"], vertex_data["ny"], vertex_data["nz"]]
        ).astype(np.float32)
    else:
        # Create zero normals if not available
        normals = np.zeros_like(vertices, dtype=np.float32)

    # Extract texture coordinates (if available)
    if "u" in vertex_data and "v" in vertex_data:
        tex_coords = np.column_stack([vertex_data["u"], vertex_data["v"]]).astype(
            np.float32
        )
    elif "s" in vertex_data and "t" in vertex_data:
        tex_coords = np.column_stack([vertex_data["s"], vertex_data["t"]]).astype(
            np.float32
        )
    else:
        # Create zero texture coordinates if not available
        tex_coords = np.zeros((len(vertices), 2), dtype=np.float32)

    # Extract face indices
    if "face" in ply_data:
        face_data = ply_data["face"]
        indices = np.array(
            [face for face in face_data["vertex_indices"]], dtype=np.uint32
        ).flatten()
    else:
        # No faces, create empty indices
        indices = np.array([], dtype=np.uint32)

    meshes.append(
        {
            "vertices": vertices,
            "normals": normals,
            "tex_coords": tex_coords,
            "indices": indices,
        }
    )

    return meshes


def load_obj(path):
    """Load OBJ file format - matches pyassimp output format"""
    raw_vertices = []
    raw_normals = []
    raw_tex_coords = []
    faces = []  # List of face tuples: (v_idx, vt_idx, vn_idx)

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if not parts:
                continue

            if parts[0] == "v":
                # Vertex position
                raw_vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == "vn":
                # Vertex normal
                raw_normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == "vt":
                # Texture coordinate
                raw_tex_coords.append([float(parts[1]), float(parts[2])])
            elif parts[0] == "f":
                # Face - parse all vertex indices
                face = []
                for i in range(1, len(parts)):
                    indices = parts[i].split("/")
                    # Vertex index (1-based, convert to 0-based)
                    v_idx = int(indices[0]) - 1
                    # Texture coordinate index (optional)
                    vt_idx = (
                        int(indices[1]) - 1 if len(indices) > 1 and indices[1] else -1
                    )
                    # Normal index (optional)
                    vn_idx = (
                        int(indices[2]) - 1 if len(indices) > 2 and indices[2] else -1
                    )
                    face.append((v_idx, vt_idx, vn_idx))

                # Triangulate if needed
                num_verts = len(face)
                if num_verts == 3:
                    faces.append(face)
                elif num_verts > 3:
                    # Fan triangulation
                    for i in range(1, num_verts - 1):
                        faces.append([face[0], face[i], face[i + 1]])

    raw_vertices = np.array(raw_vertices, dtype=np.float32)
    raw_normals = np.array(raw_normals, dtype=np.float32) if raw_normals else None
    raw_tex_coords = (
        np.array(raw_tex_coords, dtype=np.float32) if raw_tex_coords else None
    )

    # Build unique vertex combinations (like pyassimp does)
    # Each unique (v, vt, vn) combination becomes a new vertex
    unique_verts = {}
    out_vertices = []
    out_normals = []
    out_tex_coords = []
    out_indices = []

    for face in faces:
        for v_idx, vt_idx, vn_idx in face:
            key = (v_idx, vt_idx, vn_idx)
            if key not in unique_verts:
                new_idx = len(out_vertices)
                unique_verts[key] = new_idx

                # Add vertex position
                out_vertices.append(raw_vertices[v_idx])

                # Add texture coordinate
                if raw_tex_coords is not None and vt_idx >= 0:
                    out_tex_coords.append(raw_tex_coords[vt_idx])
                else:
                    out_tex_coords.append([0.0, 0.0])

                # Add normal
                if raw_normals is not None and vn_idx >= 0:
                    out_normals.append(raw_normals[vn_idx])
                else:
                    out_normals.append([0.0, 0.0, 0.0])

            out_indices.append(unique_verts[key])

    out_vertices = np.array(out_vertices, dtype=np.float32)
    out_normals = np.array(out_normals, dtype=np.float32)
    out_tex_coords = np.array(out_tex_coords, dtype=np.float32)
    out_indices = np.array(out_indices, dtype=np.uint32)

    # Generate normals if not present in the file
    if raw_normals is None or len(raw_normals) == 0:
        out_normals = np.zeros_like(out_vertices)
        indices_reshaped = out_indices.reshape(-1, 3)
        for face_indices in indices_reshaped:
            v0, v1, v2 = out_vertices[face_indices]
            normal = np.cross(v1 - v0, v2 - v0)
            norm_len = np.linalg.norm(normal)
            if norm_len > 0:
                normal = normal / norm_len
            out_normals[face_indices] += normal
        # Normalize accumulated normals
        norms = np.linalg.norm(out_normals, axis=1, keepdims=True)
        norms[norms == 0] = 1
        out_normals = out_normals / norms

    return [
        {
            "vertices": out_vertices,
            "normals": out_normals,
            "tex_coords": out_tex_coords,
            "indices": out_indices,
        }
    ]


def load_model(path):
    """Load 3D model from PLY or OBJ file"""
    ext = path.lower().split(".")[-1]

    if ext == "ply":
        return load_ply(path)
    elif ext == "obj":
        # return load_obj(path)
        # Load OBJ meshes
        print("saved")
        meshes = load_obj(path)

        # Write texture coordinates to a debug file. Use numpy.savetxt
        # to write numeric arrays; fall back to string if something fails.
        try:
            tex = meshes[0].get("tex_coords")
            if tex is None:
                raise ValueError("No tex_coords in mesh")

            # Ensure tex is a numpy array
            tex_arr = np.array(tex)

            # If tex_arr is 1D, reshape to (-1, 2) when possible
            if tex_arr.ndim == 1 and tex_arr.size % 2 == 0:
                tex_arr = tex_arr.reshape(-1, 2)

            # Save with 6 decimal places, two columns (u v)
            np.savetxt("test1.txt", tex_arr, fmt="%.6f", header="u v", comments="")
        except Exception:
            # Fallback: write a readable string representation
            with open("test1.txt", "w") as f:
                try:
                    f.write(str(meshes[0].get("tex_coords")))
                except Exception as e:
                    f.write("<failed to write tex_coords: %s>" % e)

        return meshes
    else:
        # Fallback to pyassimp for other formats
        meshes = []
        with pyassimp.load(path) as scene:
            for mesh in scene.meshes:
                vertices = np.array(mesh.vertices, dtype=np.float32)
                normals = np.array(mesh.normals, dtype=np.float32)
                tex_coords = np.array(mesh.texturecoords[0][:, :2], dtype=np.float32)

                meshes.append(
                    {
                        "vertices": vertices,
                        "normals": normals,
                        "tex_coords": tex_coords,
                        "indices": np.array(mesh.faces, dtype=np.uint32).flatten(),
                    }
                )
        # print("saved pyassuno")

        # # Write texture coordinates to a debug file. Use numpy.savetxt
        # # to write numeric arrays; fall back to string if something fails.
        # try:
        #     tex = meshes[0].get("tex_coords")
        #     if tex is None:
        #         raise ValueError("No tex_coords in mesh")

        #     # Ensure tex is a numpy array
        #     tex_arr = np.array(tex)

        #     # If tex_arr is 1D, reshape to (-1, 2) when possible
        #     if tex_arr.ndim == 1 and tex_arr.size % 2 == 0:
        #         tex_arr = tex_arr.reshape(-1, 2)

        #     # Save with 6 decimal places, two columns (u v)
        #     np.savetxt("test.txt", tex_arr, fmt="%.6f", header="u v", comments="")
        # except Exception:
        #     # Fallback: write a readable string representation
        #     with open("test.txt", "w") as f:
        #         try:
        #             f.write(str(meshes[0].get("tex_coords")))
        #         except Exception as e:
        #             f.write("<failed to write tex_coords: %s>" % e)

        # return meshes
        return meshes
