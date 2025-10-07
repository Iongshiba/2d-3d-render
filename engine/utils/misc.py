import pyassimp
import sympy as sp
import numpy as np
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


def load_texture(path):
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
    img_data = img.tobytes()

    return img_data, *(img.size)


def vertices_to_coords(vertices):
    return np.array([o.vertex.flatten() for o in vertices], dtype=np.float32)


def vertices_to_colors(vertices):
    return np.array([o.color.flatten() for o in vertices], dtype=np.float32)


def load_model(path):
    # scene = pyassimp.load(
    #     path,
    #     pyassimp.postprocess.aiProcess_Triangulate
    #     | pyassimp.postprocess.aiProcess_FlipUVs,
    # )

    meshes = []
    with pyassimp.load(path) as scene:
        for mesh in scene.meshes:
            vertices = np.array(mesh.vertices, dtype=np.float32)

            tex_coords = (
                np.array(mesh.texturecoords[0][:, :2], dtype=np.float32)
                if mesh.texturecoords.size
                else None
            )

            meshes.append(
                {
                    "vertices": vertices,
                    "tex_coords": tex_coords,
                    "indices": np.array(mesh.faces, dtype=np.uint32).flatten(),
                }
            )

    return meshes
