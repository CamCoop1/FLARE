import ast


def looks_like_path(s: str) -> bool:
    """
    Centralised function to identify what a path-like object
    should look like. Currently, this is very basic but can be
    updated later if more complexity is required.
    """
    return "/" in s or "\\" in s


def get_docstring_ranges(tree) -> list:
    """
    Return a list of (lineno, end_lineno) ranges that correspond
    to docstrings.
    """
    ranges = []

    def record_docstring(node):
        doc = ast.get_docstring(node, clean=False)
        if doc is None:
            return

        first_stmt = node.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(
            first_stmt.value, ast.Constant
        ):
            lineno = first_stmt.lineno
            end_lineno = getattr(first_stmt, "end_lineno", lineno)
            ranges.append((lineno, end_lineno))

    # Get docstring of the entire module
    record_docstring(tree)

    # Get docstrings for functions & classes
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            record_docstring(node)

    return ranges
