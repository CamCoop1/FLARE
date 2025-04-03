from pathlib import Path

import pytest

from flare.src.utils.bracket_mappings import (
    BracketMappingCMDBuilderMixin,
    BracketMappings,
    _strip,
    check_if_path_matches_mapping,
    get_suffix_from_arg,
)


@pytest.fixture(name="bracketmapping_init")
def BracketMappingCMDMixing_Instance():
    return BracketMappingCMDBuilderMixin()


@pytest.mark.parametrize(
    "name, value",
    (
        ["output", "()"],
        ["input", "--"],
        ["datatype_parameter", "++"],
        ["free_name", "<>"],
    ),
)
def test_BracketMappings_attributes(name, value):
    """Check that the required BracketMapping attributes exist"""
    assert hasattr(BracketMappings, name)
    assert getattr(BracketMappings, name) == value


@pytest.mark.parametrize("value", ("()", "--", "++", "<>"))
def test_BracketMappings_determine_bracket_mapping(value):
    """Test determine_bracket_mapping function with dummy path"""
    dummy_path = f"/hello/world/foo/bar/{value}.py"
    assert BracketMappings.determine_bracket_mapping(dummy_path) == value


def test_strip():
    dummy_path = "/hello/world/foo/bar/<>.py"
    stripped_dummy_path = "/hello/world/foo/bar/.py"
    assert _strip(dummy_path, BracketMappings.free_name) == stripped_dummy_path


@pytest.mark.parametrize("value", ("()", "--", "++", "<>"))
def test_check_if_path_matches_mapping_success(value):
    """Test that given a bracket mapping and argument, a file is found and the function
    returns True"""
    dummy_filename = f"{value}_test.py"
    dummy_path = f"/hello/world/foo/bar/{dummy_filename}"
    assert check_if_path_matches_mapping(
        arg=dummy_filename, path=dummy_path, mapping=value
    )


def test_check_if_path_matches_mapping_failure():
    """Test that given a mapping and an argument, a file that does not contain the
    argument will return False"""
    dummy_filename = "()_test.py"
    dummy_path = "/hello/world/foo/bar/"
    assert not check_if_path_matches_mapping(
        arg=dummy_filename, path=dummy_path, mapping="()"
    )


def test_get_suffix_from_arg():
    """Test that given a file name the correct suffix
    is returned
    """
    arg = "test_file.py"
    suffix = ".py"
    assert get_suffix_from_arg(arg) == suffix


@pytest.mark.parametrize(
    "method_name, is_property, dummy_arg",
    [
        ("get_file_paths", False, None),
        ("bm_output", False, None),
        ("bm_input", False, None),
        ("bm_datatype_parameter", False, "dummy_arg"),
        ("bm_free_name", False, "dummy_arg"),
    ],
)
def test_not_implemented_methods(
    bracketmapping_init, method_name, is_property, dummy_arg
):
    """Test that methods and properties raise NotImplementedError."""

    with pytest.raises(NotImplementedError):
        if is_property:
            _ = getattr(bracketmapping_init, method_name)  # Access property
        else:
            method = getattr(bracketmapping_init, method_name)  # Get method
            if dummy_arg is not None:
                method(dummy_arg)  # Call method with an argument
            else:
                method()  # Call method without arguments


def test_collect_cmd_inputs_method_calls_success(mocker):
    """Test the collect_cmd_input builder function on success"""
    # Create a mock instance of BracketMappingCMDBuilderMixin
    mock_instance = BracketMappingCMDBuilderMixin()

    # Mock the unparsed_args property to return a list with matching arguments
    mock_instance.unparsed_args = ["()", "--", "++", "<>"]

    # Mock the methods bm_output, bm_input
    mocker.patch.object(mock_instance, "bm_output", return_value=Path("/mock/output"))
    mocker.patch.object(mock_instance, "bm_input", return_value=Path("/mock/input"))
    mocker.patch.object(
        mock_instance, "bm_datatype_parameter", return_value=Path("/mock/datatype")
    )
    mocker.patch.object(
        mock_instance, "bm_free_name", return_value=Path("/mock/free_name")
    )

    # Call the method
    cmd_inputs = mock_instance.collect_cmd_inputs()

    # Assert each method was called once
    mock_instance.bm_output.assert_called_once()
    mock_instance.bm_input.assert_called_once()
    mock_instance.bm_datatype_parameter.assert_called_once()
    mock_instance.bm_free_name.assert_called_once()

    # Assert the returned cmd_inputs is as expected
    assert cmd_inputs == [
        "/mock/output",
        "/mock/input",
        "/mock/datatype",
        "/mock/free_name",
    ]


def test_collect_cmd_inputs_method_calls_failure(mocker):
    """Test the collect_cmd_input builder on failure"""
    # Create a mock instance of BracketMappingCMDBuilderMixin
    mock_instance = BracketMappingCMDBuilderMixin()

    # Mock the unparsed_args property to return a list with matching arguments
    mock_instance.unparsed_args = ["incorrect_arg"]
    # This method is used inside the stdour for the raised FileNotFoundError
    mocker.patch.object(
        mock_instance, "cmd_files_dir", return_value=Path("/mock/output")
    )

    with pytest.raises(FileNotFoundError):
        _ = mock_instance.collect_cmd_inputs()
        mock_instance.cmd_files_dir.assert_called_once()
