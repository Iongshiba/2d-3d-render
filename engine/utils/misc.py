import sympy as sp
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
    img = Image.open(path).convert("RGBA")
    img_data = img.tobytes()

    return img_data, *(img.size)
