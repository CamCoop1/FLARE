from pathlib import Path

import pytest

from flare.src.utils.dirs import find_file


@pytest.fixture
def mock_file(tmp_path):
    sample_file = tmp_path / "test.py"
    return sample_file


def test_find_file_returns_Path(mock_file):
    """Test the returned path is of type Path"""
    requested_file = find_file(mock_file)
    assert isinstance(requested_file, Path)


def test_find_file_returns_str(mock_file):
    """Test the returned path is of type str"""
    requested_file = find_file(mock_file, string=True)
    assert isinstance(requested_file, str)


def test_find_file_success_single(mock_file):
    """Test the find_file function is successful with single input"""
    find_file(mock_file)  # Test Path object
    find_file(str(mock_file))  # Test str


def test_find_file_success_multi(mock_file):
    """Test that a series of inputs to find_file returns the requested file"""
    single_inputs = str(mock_file).split("/")

    requested_file = find_file(*single_inputs, string=True)

    assert str(mock_file) in requested_file
