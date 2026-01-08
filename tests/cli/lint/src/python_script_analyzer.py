from unittest.mock import mock_open

import pytest


@pytest.fixture
def mocked_valid_python_script():
    """Mocked python script"""
    python_script = """
inputDir = "/hello/world/"
outputDir = "/world/hello"
thisDir = f"{outputDir}/files"
    """
    return python_script


def test_python_script_analyzer_for_open_call(mocked_valid_python_script, mocker):
    # Mock opened python file
    mock_open_func = mocker.path("builtins.open", mock_open())

    # Setup mock responses for the open call
    mock_open_func.side_effect = [
        mock_open(read_data=mocked_valid_python_script()).return_value
    ]
