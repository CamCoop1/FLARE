from pathlib import Path
from unittest.mock import mock_open

import pytest
import yaml

from flare.src.utils.yaml import (  # Make sure to import get_config from the correct location
    get_config,
)


@pytest.fixture
def mock_find_file(mocker):
    """Mock the find_file function"""
    return mocker.patch("flare.src.utils.yaml.find_file")


@pytest.fixture
def setup_parameters():
    """Setup parameters for mock testing"""
    default_dir_parameter = "tmp"
    # Mock yaml path
    yaml_path = Path(f"{default_dir_parameter}/config.yaml")
    # Mock schema path
    model_name = "UserMCProdConfigModel"
    return default_dir_parameter, yaml_path, model_name


def test_get_config_no_model(mock_find_file, setup_parameters, mocker):
    """Test when valid config and no schema, returned value is as expected"""
    _, yaml_path, _ = setup_parameters
    # Prepare mock responses for find_file
    mock_find_file.side_effect = [yaml_path]  # For YAML file

    # Mock YAML file content
    mock_open_func = mocker.patch("builtins.open", mock_open())

    # Set up mock responses for open (first for YAML, then for JSON)
    mock_open_func.side_effect = [
        mock_open(read_data=yaml.dump({"key": "value"})).return_value
    ]

    result = get_config(yaml_path.stem)

    assert result == {"key": "value"}
    mock_find_file.assert_any_call(
        "analysis/config", Path(yaml_path.stem).with_suffix(".yaml")
    )
    # Ensure no schema is checked
    assert mock_find_file.call_count == 1  # Only called once for the YAML file
    assert mock_open_func.call_count == 1  # Only called once to open YAML file
