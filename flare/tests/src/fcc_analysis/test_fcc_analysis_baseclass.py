from pathlib import Path
from unittest.mock import MagicMock

import pytest
from src.fcc_analysis.fcc_analysis_baseclass import (
    FCCAnalysisBaseClass,
    FCCTemplateMethodMixin,
)
from src.fcc_analysis.fcc_stages import Stages

"""
FCCTemplateMethodMixin Tests
"""


# Create a minimal test class to use the mixin
class TestStage(FCCTemplateMethodMixin):
    stage = MagicMock(name="mock_stage")  # Mock stage

    @property
    def output_dir(self):
        return "test_output_dir"

    def get_input_file_names(self):
        return {"test": ["test_input_file.root"]}


@pytest.fixture
def test_instance(mocker):
    """Fixture to create a TestStage instance with mocks."""
    instance = TestStage()
    mocker.patch(
        "src.fcc_analysis.fcc_analysis_baseclass.find_file",
        side_effect=lambda *args: Path("/mocked/path") / args[-1],
    )
    return instance


def test_abstract_methods():
    """Ensure abstract methods raise NotImplementedError."""
    instance = FCCTemplateMethodMixin()
    with pytest.raises(NotImplementedError):
        _ = instance.output_dir
    with pytest.raises(NotImplementedError):
        _ = instance.get_input_file_names()


def test_inputDir_path_for_is_file_False(mocker, test_instance):
    """Test inputDir_path when the file exists and is not a file i.e a directory"""
    # Create a mock Path object that is returned by find_file
    mock_file = mocker.MagicMock(spec=Path)
    # Mock the str() to return the expected output
    mock_file.__str__.return_value = "/mocked/path/mock_output.root"
    # Set the is_file return value to False
    mock_file.is_file.return_value = False

    mock_find_file = mocker.patch(
        "src.fcc_analysis.fcc_analysis_baseclass.find_file", return_value=mock_file
    )

    assert test_instance.inputDir_path == "/mocked/path/mock_output.root"
    assert mock_find_file.called_once_with(mock_file)


def test_inputDir_path_for_is_file_True(mocker, test_instance):
    """Test inputDir_path when the file exists and is a file"""
    # Create a mock Path object that is returned by find_file
    mock_file = mocker.MagicMock(spec=Path)
    # Set the is_file to True
    mock_file.is_file.return_value = True
    # Set the parent to be type Path
    mock_file.parent = Path("/mocked/path")

    mock_find_file = mocker.patch(
        "src.fcc_analysis.fcc_analysis_baseclass.find_file", return_value=mock_file
    )

    assert test_instance.inputDir_path == "/mocked/path"
    assert mock_find_file.called_once_with(mock_file)


def test_rendered_template_path(test_instance, mocker):
    """Test rendered_template_path property."""
    # Mock the stage name
    test_instance.stage.name = "test_stage"
    # Create the dummy output path
    output_path = Path(
        f"{test_instance.output_dir}/steering_{test_instance.stage.name}.py"
    )
    # Mock the first find_file call inside rendered_template_path
    mock_find_file = mocker.patch(
        "src.fcc_analysis.fcc_analysis_baseclass.find_file", return_value=output_path
    )

    assert (
        test_instance.rendered_template_path == output_path
    )  # Check the output is correct
    assert mock_find_file.called_once_with(
        output_path.parent, Path(output_path.name)
    )  # Check the find_file was called


@pytest.mark.parametrize(
    "read_data, match, stage",
    (
        # outputDir in any stage other than plot
        [
            "outputDir = 'some/path'",
            "Please do not define your own output directory",
            "stage1",
        ],
        # outDir for plot stage
        [
            "outdir = 'some/path'",
            "Please do not define your own output directory",
            "plot",
        ],
    ),
)
def test_run_templating_assertions_for_outputDir(
    test_instance, mocker, read_data, match, stage
):
    """Test assertions in run_templating method when passed outputDir or outdir. Should never
    define their own outputDir as b2luigi will handle this"""
    test_instance.stage = Stages[stage]
    mock_stage_script = mocker.patch.object(
        Stages, "get_stage_script", return_value=Path("/mocked/path/stage_script.py")
    )
    mock_open = mocker.mock_open(read_data=read_data)
    mocked_open = mocker.patch("pathlib.Path.open", mock_open)

    with pytest.raises(AssertionError, match=match):
        test_instance.run_templating()
        assert mock_stage_script.called_once_with(test_instance.stage)
        assert mocked_open.called_once_with("r'")


@pytest.mark.parametrize(
    "read_data, match, requires",
    (
        # inputDir when no dependency i.e requires function returns [], should define input
        ["", "Please define your own input directory in your", False],
        # inputDir when dependency required, i.e should not define your own input
        [
            "inputDir = 'some/path'",
            "Please do not define your own input directory",
            True,
        ],
    ),
)
def test_run_templating_assertions_for_inputDir(
    test_instance, mocker, read_data, match, requires
):
    """Test assertions in run_templating method when passed inputDir"""
    # Set the requires function to return an empty list of it DOESN'T have a requirement
    test_instance.requires = lambda: ["mock"] if requires else []
    # Patch the get_stage_script to return a mocked Path
    mock_stage_script = mocker.patch.object(
        Stages, "get_stage_script", return_value=Path("/mocked/path/stage_script.py")
    )
    # Mock the open function to return our read_data passes from parametrize
    mock_open = mocker.mock_open(read_data=read_data)
    mocked_open = mocker.patch("pathlib.Path.open", mock_open)

    with pytest.raises(AssertionError, match=match):
        test_instance.run_templating()
        assert mock_stage_script.called_once_with(test_instance.stage)
        assert mocked_open.called_once_with("r'")


@pytest.mark.parametrize(
    "read_data, requires",
    (
        # For a task with no requires
        ["inputDir = 'Hello world'", False],
        # For a task with no requires
        ["Hello world", True],
    ),
)
def test_run_templating_success(test_instance, mocker, read_data, requires):
    """Test successful execution of run_templating."""
    # Mock the get_stage_script from the Stages function
    mock_stage_script = mocker.patch.object(
        Stages, "get_stage_script", return_value=Path("/mocked/path/stage_script.py")
    )

    # Create the mocked open
    mock_open = mocker.mock_open(read_data=read_data)
    mocked_open = mocker.patch("pathlib.Path.open", mock_open)

    # Mock the shutil.copy2 function
    mock_shutil_copy = mocker.patch("shutil.copy2")
    test_instance.requires = lambda: ["mock"] if requires else []

    # Run templating
    test_instance.run_templating()
    # Check that the open function was called with r
    mocked_open.assert_any_call("r")
    if not requires:
        # Check open was only called once
        assert mocked_open.call_count == 1
        # Check the shutil.copy2 function was called with correct parameters
        mock_shutil_copy.assert_called_once_with(
            mock_stage_script.return_value, test_instance.rendered_template_path
        )
    else:
        # Check open was called twice since a rendered template is required
        assert mocked_open.call_count == 2
        # Check the open function was called with w
        mocked_open.assert_any_call("w")


"""
FCCAnalysisBaseClass Tests
"""


def test_FCCAnalysisBaseClass_output_dir_name_success(mocker):
    """Test the output_dir_name property to ensure it returns the correct value"""
    mocker.patch.object(
        FCCAnalysisBaseClass,
        "stage_dict",
        new_callable=mocker.PropertyMock,
        return_value={"output_file": "mocked"},
    )
    test_instance = FCCAnalysisBaseClass()

    assert test_instance.output_dir_name == "mocked"


def test_FCCAnalysisBaseClass_unparsed_args_success(mocker):
    """Test the unparsed_args property to ensure it returns the correct value"""
    mocker.patch.object(
        FCCAnalysisBaseClass,
        "stage_dict",
        new_callable=mocker.PropertyMock,
        return_value={"args": "mocked"},
    )
    test_instance = FCCAnalysisBaseClass()

    assert test_instance.unparsed_args == "mocked"


def test_FCCAnalysisBaseClass_output_dir(mocker):
    """Test the _unparsed_output_file_name property to ensure it returns the correct value"""
    mocked_path = Path("mocked/path")
    mocker.patch.object(
        FCCAnalysisBaseClass, "get_output_file_name", return_value=str(mocked_path)
    )
    test_instance = FCCAnalysisBaseClass()
    test_instance.stage = Stages.stage1

    # The returned output_dir is an absolute path
    assert str(mocked_path) in str(test_instance.output_dir)


def test_FCCAnalysisBaseClass_bm_free_name_returns_rendered_template_path():
    """Test the bm_free_name function for the BracketMappingMixin returns the rendered_template_path
    from the TemplateMixin"""
    test_instance = FCCAnalysisBaseClass()
    test_instance.stage = Stages.stage1

    assert test_instance.bm_free_name() == test_instance.rendered_template_path


def test_FCCAnalysisBaseClass_run_fcc_analysis_stage(mocker):
    """Check that the run_fcc_analysis_stage called pre_run, subprocess.check_call with appropriate
    inputs and the on_completion method"""
    mock_pre_run = mocker.patch.object(FCCAnalysisBaseClass, "pre_run")
    mock_subprocess = mocker.patch("subprocess.check_call")
    mock_on_completion = mocker.patch.object(FCCAnalysisBaseClass, "on_completion")

    test_instance = FCCAnalysisBaseClass()
    test_instance.stage = Stages.stage1

    test_instance.run_fcc_analysis_stage()

    mock_pre_run.assert_called_once()
    mock_subprocess.assert_called_once_with(
        test_instance.prod_cmd, cwd=test_instance.output_dir, shell=True
    )
    mock_on_completion.assert_called_once()


def test_FCCAnalysisBaseClass_process_success(mocker):
    """Test the process function to ensure the making of directories, templating and fcc running is done"""
    mock_run_templating = mocker.patch.object(FCCAnalysisBaseClass, "run_templating")
    mock_run_fcc_analysis_stage = mocker.patch.object(
        FCCAnalysisBaseClass, "run_fcc_analysis_stage"
    )
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    # When mocking mkdir must also patch the os.replace function
    mocker.patch("os.replace")

    test_instance = FCCAnalysisBaseClass()
    test_instance.stage = Stages.stage1

    test_instance.process()

    mock_run_templating.assert_called_once()
    mock_run_fcc_analysis_stage.assert_called_once()
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
