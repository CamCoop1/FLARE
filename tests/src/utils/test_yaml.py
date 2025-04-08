from pathlib import Path
from unittest.mock import mock_open

import pytest
import yaml
from pydantic import BaseModel

from flare.src.utils.yaml import (  # Make sure to import get_config from the correct location
    get_config,
)


@pytest.fixture
def mock_find_file(mocker):
    """Mock the find_file function"""
    return mocker.patch("flare.src.utils.yaml.find_file")


@pytest.fixture
def mock_model():
    """Mock Pydantic BaseModel"""

    class MockModel(BaseModel):
        name: str

    return MockModel


@pytest.fixture
def setup_parameters(mock_model):
    """Setup parameters for mock testing"""
    default_dir_parameter = "tmp"
    # Mock yaml path
    yaml_path = Path(f"{default_dir_parameter}/config.yaml")
    # Mock models dict
    models = {mock_model.__name__: mock_model}
    return default_dir_parameter, yaml_path, models


def test_get_config_for_valid_model(mock_find_file, setup_parameters, mocker):
    """Test given a valid model and input data, the returned value is a dictionary"""
    _, yaml_path, models = setup_parameters

    model_name = next(iter(models.keys()))
    # Mock the find_file call to return the yaml path
    mock_find_file.return_value = yaml_path

    # Mock the models dictionary
    mocker.patch.dict("flare.src.utils.yaml.models", models)
    # Mock YAML file content
    mock_open_func = mocker.patch("builtins.open", mock_open())

    # Set up mock responses for open (first for YAML, then for JSON)
    mock_open_func.side_effect = [
        mock_open(
            read_data=yaml.dump({"name": "value", "$model": model_name})
        ).return_value
    ]
    get_config.cache_clear()
    result = get_config(yaml_path.stem)

    mock_find_file.assert_called_once()
    mock_open_func.assert_called_once()  # Only called once to open YAML file
    assert isinstance(result, dict)
    assert result == {"name": "value"}


def test_get_config_for_invalid_model_raises_KeyError(
    mock_find_file, setup_parameters, mocker
):
    """Test given an invalid model, a KeyError is raised"""
    _, yaml_path, _ = setup_parameters

    # Mock the find_file call to return the yaml path
    mock_find_file.return_value = yaml_path

    # Mock YAML file content
    mock_open_func = mocker.patch("builtins.open", mock_open())

    # Set up mock responses for open (first for YAML, then for JSON)
    mock_open_func.side_effect = [
        mock_open(
            read_data=yaml.dump({"name": "value", "$model": "invalid"})
        ).return_value
    ]

    with pytest.raises(KeyError):
        get_config.cache_clear()
        _ = get_config(yaml_path.stem)

    mock_find_file.assert_called_once()
    mock_open_func.assert_called_once()  # Only called once to open YAML file


def test_get_config_no_model(mock_find_file, setup_parameters, mocker):
    """Test when valid config and no model, returned value is as expected"""
    _, yaml_path, _ = setup_parameters
    # Prepare mock responses for find_file
    mock_find_file.side_effect = [yaml_path]  # For YAML file

    # Mock YAML file content
    mock_open_func = mocker.patch("builtins.open", mock_open())

    # Set up mock responses for open (first for YAML, then for JSON)
    mock_open_func.side_effect = [
        mock_open(read_data=yaml.dump({"key": "value"})).return_value
    ]

    get_config.cache_clear()
    result = get_config(yaml_path.stem)

    assert result == {"key": "value"}
    mock_find_file.assert_any_call(
        "analysis/config", Path(yaml_path.stem).with_suffix(".yaml")
    )
    # Ensure no schema is checked
    mock_find_file.assert_called_once()  # Only called once for the YAML file
    mock_open_func.assert_called_once()  # Only called once to open YAML file
