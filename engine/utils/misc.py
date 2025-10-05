import sympy as sp


def make_numpy_func(expr, vars=("x", "y")):
    # Define symbols for all variable names
    symbols = sp.symbols(vars)
    # Parse the expression safely
    sym_expr = sp.sympify(expr)
    # Convert symbolic expression to NumPy function
    f = sp.lambdify(symbols, sym_expr, modules=["numpy"])
    return f
