import ast
from pathlib import Path

import pytest

from flare.cli.lint.src.utils import get_docstring_ranges, looks_like_path

global VALID_DOC_RANGES


@pytest.fixture
def valid_path() -> str:
    return "/hello/world/"


@pytest.fixture
def python_script_as_string_and_ranges() -> tuple:
    """
    Here we import the dummy script along with parsing of the valid ranges
    """
    file_path = Path(__file__).parent / "dummy_script.py"

    with file_path.open() as f:
        file_contents = f.read()

    file_lines = file_contents.splitlines()

    # Here we do the parsing of the valid ranges
    unparsed_valid_ranges = file_lines.pop(0).split(",")[1:]
    parsed_valid_ranges: list[tuple[int]] = []
    for unparsed_range in unparsed_valid_ranges:
        # If it has .. indicates there are different start and end lines
        unparsed_range = unparsed_range.split("..")
        # Use a match statement to breakdown our two options, 1 or 2
        match len(unparsed_range):
            case 1:
                range = int(unparsed_range[0])
                parsed_valid_ranges.append((range, range))
            case 2:
                start, end = tuple(map(int, unparsed_range))
                parsed_valid_ranges.append((start, end))
            case _:
                continue

    return (file_contents, str(file_path), parsed_valid_ranges)


@pytest.fixture
def get_valid_AST_tree(python_script_as_string_and_ranges):
    source, path = python_script_as_string_and_ranges[:2]
    return ast.parse(source, filename=path)


def test_valid_looks_like_path(valid_path):
    """Test that a valid path returns True `looks_like_path`"""
    assert looks_like_path(valid_path)


def test_invalid_looks_like_path(valid_path):
    """Test that an invalid path returns False for `looks_like_path`"""
    invalid_path = valid_path.replace("/", "")
    assert not looks_like_path(invalid_path)


def test_get_doc_string_ranges_for_correct_lines(
    python_script_as_string_and_ranges, get_valid_AST_tree
):
    """Test that the doc-string valid ranges function correctly identifies
    the lines in which docstrings are present."""
    valid_ranges = python_script_as_string_and_ranges[-1]
    tree = get_valid_AST_tree

    ranges = get_docstring_ranges(tree)
    assert ranges == valid_ranges
