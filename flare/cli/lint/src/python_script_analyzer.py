import ast
from typing import Dict, Protocol

from flare.cli.lint.src.pydantic_models import AnalyzerModel
from flare.cli.lint.src.utils import get_docstring_ranges, looks_like_path


class Registry(Protocol):
    @property
    def VALID_VARIABLE_KEYS(self) -> set: ...

    @classmethod
    def initialize_register_mode(cls): ...

    @classmethod
    def register_flaggable_variable(cls, name: str, value: str, lineno: int): ...

    @classmethod
    def register_identified_path_variables(
        cls,
        name: str,
        path: str,
        is_fstring: bool,
        references: list,
        noqa: bool,
        lineno: int,
        end_lineno: int,
    ): ...

    @classmethod
    def registered_identified_path_variables(cls) -> dict: ...

    @classmethod
    def validate_registered_data(cls): ...


class Visitor(ast.NodeVisitor):
    def __init__(
        self, *args, lines: list, docstring_ranges: list, registry: Registry, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.lines = lines
        self.registry = registry
        self.docstring_ranges = docstring_ranges

    def is_in_docstring(self, node) -> bool:
        lineno = node.lineno
        end_lineno = getattr(node, "end_lineno", lineno)
        for start, end in self.docstring_ranges:
            if lineno >= start and end_lineno <= end:
                return True
        return False

    def has_noqa(self, node) -> bool:
        for lineno in range(node.lineno - 1, getattr(node, "end_lineno", node.lineno)):
            if any(x in self.lines[lineno] for x in ["noqa", "#"]):
                return True
        return False

    def visit_Assign(self, node):
        if self.is_in_docstring(node):
            return

        value_info = self._analyze_value(node.value)
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            name = target.id
            if name in self.registry.VALID_VARIABLE_KEYS:
                self.registry.register_flaggable_variable(
                    name=name, value=value_info["raw"], lineno=node.lineno
                )
            if value_info["is_path"]:
                self.registry.register_identified_path_variables(
                    name=name,
                    path=value_info["raw"],
                    is_fstring=value_info["is_fstring"],
                    references=value_info["refs"],
                    noqa=self.has_noqa(node),
                    lineno=node.lineno,
                    end_lineno=node.end_lineno or node.lineno,
                )
        self.generic_visit(node)

    def _analyze_value(self, node):
        # Check for unformatted string
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {
                "is_path": looks_like_path(node.value),
                "raw": node.value,
                "is_fstring": False,
                "refs": [],
            }

        # Check for formatted f-string
        if isinstance(node, ast.JoinedStr):
            full_string = []
            parts, refs = [], []
            for v in node.values:
                if isinstance(v, ast.Constant):
                    parts.append(v.value)
                    full_string.append(v.value)
                elif isinstance(v, ast.FormattedValue) and isinstance(
                    v.value, ast.Name
                ):
                    refs.append(v.value.id)
                    full_string.append("{" + v.value.id + "}")
            combined = "".join(parts)
            full_assigned_string = "".join(full_string)
            return {
                "is_path": looks_like_path(combined),
                "raw": full_assigned_string,
                "is_fstring": True,
                "refs": refs,
            }

        if (
            isinstance(node, ast.Name)
            and node.id in self.registry.registered_identified_path_variables()
        ):
            return {
                "is_path": True,
                "raw": None,
                "is_fstring": False,
                "refs": [node.id],
            }
        return {"is_path": False, "raw": None, "is_fstring": False, "refs": []}


def analyze_python_script(path: str) -> Dict:
    with open(path) as f:
        source = f.read()
    # Built list of lines for script
    lines = source.splitlines()
    # Build the Analytic Syntax Tree
    tree = ast.parse(source, filename=path)
    # Get the ranges which encompass the docstrings of the script
    docstring_ranges = get_docstring_ranges(tree)
    # Initialize a AnalyzerModel for us to build from
    result_registry = AnalyzerModel.initialize_register_mode()
    # Visit the AST and build our AnalyzerModel database
    Visitor(
        lines=lines, docstring_ranges=docstring_ranges, registry=result_registry
    ).visit(tree)
    # Validate the data found via Visitor and return the Pydantic Model
    return result_registry.validate_registered_data()


if __name__ == "__main__":
    script = "/remote/nas00-1/users/charris/phd/fcc/FLARE-examples/analysis/studies/higgs_mass_example/stage1_flavor.py"
    analysis = analyze_python_script(script)
    print(analysis.flaggable_variables)
