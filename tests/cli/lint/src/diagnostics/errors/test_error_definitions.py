import pytest

from flare.cli.lint.src.diagnostics.errors import definitions


@pytest.mark.parametrize("method", ["ErrorLevel", "ErrorExceptions", "Error"])
def test_defintions_contains_expected_classes(method):
    """Check the the definitions module has the expected classes inside"""
    assert hasattr(definitions, method)
