import json
from pathlib import Path
from unittest.mock import mock_open

import jsonschema
import pytest
import yaml

from flare.src.utils.yaml import (  # Make sure to import get_config from the correct location
    get_config,
)


@pytest.fixture
def mock_find_file(mocker):
    """Mock the find_file function"""
    return mocker.patch("src.utils.yaml.find_file")


@pytest.fixture
def setup_parameters():
    """Setup parameters for mock testing"""
    default_dir_parameter = "tmp"
    # Mock yaml path
    yaml_path = Path(f"{default_dir_parameter}/config.yaml")
    # Mock schema path
    schema_path = Path(f"{default_dir_parameter}/schema.json")
    return default_dir_parameter, yaml_path, schema_path


def test_get_config_success(mock_find_file, setup_parameters, mocker):
    """Test when valid config and schema, returned value is as expected"""
    default_dir_parameter, yaml_path, schema_path = setup_parameters
    # Prepare mock responses for find_file
    mock_find_file.side_effect = [
        yaml_path,  # For YAML file
        schema_path,  # For schema file
    ]

    # Mock YAML file content
    mock_open_func = mocker.patch("builtins.open", mock_open())

    # Set up mock responses for open (first for YAML, then for JSON)
    mock_open_func.side_effect = [
        mock_open(
            read_data=yaml.dump({"$schema": str(schema_path), "key": "value"})
        ).return_value,
        mock_open(
            read_data=json.dumps(
                {
                    "type": "object",
                    "properties": {"key": {"type": "string"}},
                    "required": ["key"],
                }
            )
        ).return_value,
    ]

    # Call the function
    result = get_config(yaml_path.stem, dir=default_dir_parameter)

    # Validate the result
    assert result == {"key": "value"}  # Ensure the returned value is as expected
    assert mock_open_func.call_count == 2  # check the open function was called twice
    mock_find_file.assert_any_call(
        default_dir_parameter, Path(yaml_path.stem).with_suffix(".yaml")
    )  # Ensure find_file was called with correct yaml path
    mock_find_file.assert_any_call(
        str(schema_path)
    )  # Ensure find_file was called with correct schema path
    mock_open_func.assert_any_call(yaml_path)  # Ensure open was called on the YAML file
    mock_open_func.assert_any_call(
        schema_path
    )  # Ensure open was called on the schema file


def test_get_config_schema_validation_fail(mock_find_file, setup_parameters, mocker):
    """Test when invalid config and schema, jsonschema.ValidationError is raised"""
    _, yaml_path, schema_path = setup_parameters
    # Prepare mock responses for find_file
    mock_find_file.side_effect = [
        yaml_path,  # For YAML file
        schema_path,  # For schema file
    ]

    # Mock YAML file content
    mock_open_func = mocker.patch("builtins.open", mock_open())

    # Set up mock responses for open (first for YAML, then for JSON)
    mock_open_func.side_effect = [
        mock_open(
            read_data=yaml.dump({"$schema": str(schema_path), "invalid": "value"})
        ).return_value,
        mock_open(
            read_data=json.dumps(
                {
                    "type": "object",
                    "properties": {"key": {"type": "string"}},
                    "required": ["key"],
                }
            )
        ).return_value,
    ]

    # Ensure jsonschema validation fails
    with pytest.raises(jsonschema.ValidationError):
        get_config(yaml_path.stem)


def test_get_config_no_schema(mock_find_file, setup_parameters, mocker):
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
