from typing import Protocol
from unittest.mock import mock_open

import pytest

from flare.cli.lint.src import python_script_analyzer
from flare.src.pydantic_models.utils import ForbidExtraBaseModel


@pytest.fixture
def mocked_valid_python_script():
    """Mocked python script"""
    python_script = """inputDir = "/hello/world/"
outputDir = "/world/hello"
thisDir = f"{outputDir}/files"
    """
    return python_script


@pytest.fixture
def generic_data(mocker, mocked_valid_python_script):
    """Mocked generic data returned by the analyze_python_script
    Uses the defined python script from mocked_valid_python_script"""
    # Mock opened python file
    _ = mocker.patch("builtins.open", mock_open(read_data=mocked_valid_python_script))

    return python_script_analyzer.analyze_python_script("")


def test_assert_Registry_protocol_exists():
    """Test the the python_script_analyzer has a Registry class.
    Check the attributes of the Registry class"""
    # Check the Registry class exists
    assert hasattr(python_script_analyzer, "Registry")
    registry = python_script_analyzer.Registry
    # Check the Registry class is a Protocol
    assert issubclass(registry, Protocol)
    # Ensure all the methods and properties of the Protocol as in place.
    assert hasattr(registry, "initialize_register_mode")
    assert hasattr(registry, "register_flaggable_variable")
    assert hasattr(registry, "register_identified_path_variables")
    assert hasattr(registry, "registered_identified_path_variables")
    assert hasattr(registry, "validate_registered_data")
    assert hasattr(registry, "VALID_VARIABLE_KEYS")


def test_python_script_analyzer_analyze_python_script_for_open_call_and_return_object(
    mocked_valid_python_script, mocker
):
    """Test the analyze_python_script function for a single call to `open` and
    that the returned object is of type ForbidExtraBaseModel"""
    # Mock opened python file
    mock_open_func = mocker.patch(
        "builtins.open", mock_open(read_data=mocked_valid_python_script)
    )

    data = python_script_analyzer.analyze_python_script("")
    mock_open_func.assert_called_once()
    assert isinstance(data, ForbidExtraBaseModel)


def test_python_script_analyzer_analyze_python_script_return_object_flaggable_variables(
    generic_data,
):
    """Test the analyze_python_script functions return object, ensuring it has
    properly captured the `flaggable_variables`"""
    assert len(generic_data.flaggable_variables) == 2
    assert all(
        x in generic_data.flaggable_variables.keys() for x in ["inputDir", "outputDir"]
    )

    assert generic_data.flaggable_variables["inputDir"].value == "/hello/world/"
    assert generic_data.flaggable_variables["inputDir"].lineno == 1

    assert generic_data.flaggable_variables["outputDir"].value == "/world/hello"
    assert generic_data.flaggable_variables["outputDir"].lineno == 2


def test_python_script_analyzer_analyze_python_script_return_object_identified_path_variables(
    generic_data,
):
    """Test the analyzer_python_script function return object, ensuring it has
    properly capture the `identified_path_variables`"""
    assert len(generic_data.identified_path_variables) == 3
    assert all(
        x in generic_data.identified_path_variables.keys()
        for x in ["inputDir", "outputDir", "thisDir"]
    )
    assert generic_data.identified_path_variables["thisDir"].is_fstring
    assert all(
        x in generic_data.identified_path_variables["thisDir"].references
        for x in ["outputDir"]
    )
    assert all(
        x in generic_data.identified_path_variables["thisDir"].references
        for x in ["outputDir"]
    )
