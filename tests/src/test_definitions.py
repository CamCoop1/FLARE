from pathlib import Path

import flare.src.definitions as defs


def test_definitions_contains_BASE_DIRECTORY():
    """
    Test that the definitions module has BASE_DIRECTORY
    """
    assert hasattr(defs, "BASE_DIRECTORY")


def test_BASE_DIRECTORY_returns_correct_location():
    """
    Test the BASE_DIRECTORY variable points to the root of FLARE
    """
    assert defs.BASE_DIRECTORY == Path(__file__).parents[2]
