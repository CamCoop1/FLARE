import pytest

from flare.cli.lint.src.diagnostics.errors import error_registry


def test_errors_registry_has_FlareErrors():
    """Ensure the FlareErrors registry is located in the error_registry module"""
    assert hasattr(error_registry, "FlareErrors")


@pytest.mark.parametrize(
    "method",
    ["checker_func", "specific_error_exceptions"],
)
def test_FlareErrors_for_structure(method):
    """Check FlareErrors has required helper functions"""
    flare_errors = error_registry.FlareErrors

    assert hasattr(flare_errors, method)
