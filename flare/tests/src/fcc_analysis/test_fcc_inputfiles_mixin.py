from pathlib import Path

import pytest
from src.fcc_analysis.fcc_inputfiles_mixin import FCCInputFilesMixin


@pytest.fixture
def mock_class(tmp_path):
    class Dummy(FCCInputFilesMixin):
        output_dir = tmp_path / "output"

        def get_output_file_name(self, key: str):
            return f"output_{key}.root"

    return Dummy()


def test_copy_input_file_to_output_dir(mocker, mock_class):
    """Test the the copy_input_file_to_output_dir is working as expected by mocking the find_file and shutil.copy"""
    # Create the source file path
    source_file_path = Path("tmp/source_file.root")
    # Mock the find_file function to return our source_file_path
    mock_find_file = mocker.patch(
        "src.fcc_analysis.fcc_inputfiles_mixin.find_file", return_value=source_file_path
    )
    # Mock the shutil.copy function as to not actually copy anything
    mock_shutil_copy = mocker.patch("shutil.copy")
    # Call copy_input_file_to_output_dir from our mock class
    mock_class.copy_input_file_to_output_dir(source_file_path)
    # Check that find_file was called once with our source_file_path
    mock_find_file.assert_called_once_with(source_file_path)
    # Check that shuil_copy was called once with our source_file_path and the correct destination
    mock_shutil_copy.assert_called_once_with(
        source_file_path, Path(mock_class.output_dir) / source_file_path.name
    )


def test_copy_inputfiles_declared_in_stage_script_with_inputPaths(mocker, mock_class):
    """Test that when inputPaths are included,"""
    # Mock the Stages.get_stage_script function
    mock_stage_script = mocker.patch(
        "src.fcc_analysis.fcc_inputfiles_mixin.Stages.get_stage_script"
    )

    # Mock `Stages.get_stage_script` to return a Path object
    mock_stage_path = Path("/tmp/stages/test_stage.py")
    mock_stage_script.return_value = mock_stage_path

    # Mock `.open()` to return the expected file content
    mock_open = mocker.mock_open(
        read_data='includePaths = ["file1.root", "file2.root"]'
    )
    mocker.patch("pathlib.Path.open", mock_open)

    mock_copy = mocker.patch.object(mock_class, "copy_input_file_to_output_dir")

    mock_class.stage = "test_stage"
    mock_class.copy_inputfiles_declared_in_stage_script()

    assert mock_copy.call_count == 2

    mock_copy.assert_any_call("/tmp/stages/file1.root")
    mock_copy.assert_any_call("/tmp/stages/file2.root")


def test_copy_inputfiles_declared_in_stage_script_with_no_inputPaths(
    mocker, mock_class
):
    """Test that when not inputPaths are included, the copy_input_files_to_output_dir is not called"""
    # Mock the Stages.get_stage_script function
    mock_stage_script = mocker.patch(
        "src.fcc_analysis.fcc_inputfiles_mixin.Stages.get_stage_script"
    )

    # Mock `Stages.get_stage_script` to return a Path object
    mock_stage_path = Path("/tmp/stages/test_stage.py")
    mock_stage_script.return_value = mock_stage_path

    # Mock `.open()` to return the expected file content, in this case not an includePaths
    mock_open = mocker.mock_open(read_data="Hello world")
    mocker.patch("pathlib.Path.open", mock_open)

    mock_copy = mocker.patch.object(mock_class, "copy_input_file_to_output_dir")

    mock_class.stage = "test_stage"
    mock_class.copy_inputfiles_declared_in_stage_script()

    assert mock_copy.call_count == 0
