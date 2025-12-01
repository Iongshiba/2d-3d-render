# import pyassimp
import sympy as sp
import numpy as np
import pyassimp
from OpenGL import GL
from PIL import Image


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


def load_model(path):
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

    return meshes
