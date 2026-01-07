import ast
from typing import Dict

from flare.cli.lint.src.pydantic_models import AnalyzerModel
from flare.cli.lint.utils import get_docstring_ranges, looks_like_path


def analyze_python_script(path: str) -> Dict:
    with open(path) as f:
        source = f.read()
    lines = source.splitlines()
    tree = ast.parse(source, filename=path)
    docstring_ranges = get_docstring_ranges(tree)

    result_registry = AnalyzerModel.initialize_register_mode()

    def has_noqa(node):
        for lineno in range(node.lineno - 1, getattr(node, "end_lineno", node.lineno)):
            if any(x in lines[lineno] for x in ["noqa", "#"]):
                return True
        return False

    def is_in_docstring(node):
        lineno = node.lineno
        end_lineno = getattr(node, "end_lineno", lineno)
        for start, end in docstring_ranges:
            if lineno >= start and end_lineno <= end:
                return True
        return False

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if is_in_docstring(node):
                return

            value_info = self._analyze_value(node.value)
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                name = target.id
                if name in result_registry.VALID_VARIABLE_KEYS:
                    result_registry.register_flaggable_variable(
                        name=name, value=value_info["raw"], lineno=node.lineno
                    )
                if value_info["is_path"]:
                    result_registry.register_identified_path_variables(
                        name=name,
                        path=value_info["raw"],
                        is_fstring=value_info["is_fstring"],
                        references=value_info["refs"],
                        noqa=has_noqa(node),
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
                and node.id in result_registry.registered_identified_path_variables()
            ):
                return {
                    "is_path": True,
                    "raw": None,
                    "is_fstring": False,
                    "refs": [node.id],
                }
            return {"is_path": False, "raw": None, "is_fstring": False, "refs": []}

    Visitor().visit(tree)
    return result_registry.validate_registered_data()


if __name__ == "__main__":
    script = "/remote/nas00-1/users/charris/phd/fcc/FLARE-examples/analysis/studies/higgs_mass_example/stage1_flavor.py"
    analysis = analyze_python_script(script)
    print(analysis.flaggable_variables)
