from enum import Enum
from itertools import combinations
from pathlib import Path

import pytest
from src.fcc_analysis.fcc_stages import Stages, _Stages


@pytest.fixture
def ordered_permutations():
    stages_list = list(Stages)
    first_element = stages_list[0]
    return [
        list(subseq)
        for r in range(1, len(stages_list) + 1)
        for subseq in combinations(stages_list, r)
        if subseq[0] == first_element
    ]


def test__Stages_issubclass_of_Enum():
    """Test the _Stages class is a child of Enum"""
    assert issubclass(_Stages, Enum)


def test_Stages_issubclass_of__Stages():
    """Test the Stages class is a subclass of _Stages )"""
    assert issubclass(Stages, _Stages)


@pytest.mark.parametrize(
    "method",
    [
        "capitalize",
        "_get_steering_script_names",
        "_get_active_stages",
        "check_for_unregistered_stage_file",
        "get_stage_script",
        "get_stage_ordering",
    ],
)
def test__Stages_has_correct_attributes(method):
    """Test _Stages class has required methods"""
    assert hasattr(_Stages, method)


def test_fcc_Stages_returns_capitalised_name():
    """Test that for each  variant of the enum, there is a captialize function and it
    returns the variant name capitalized"""
    for stage in Stages:
        assert stage.capitalize()  # Will raise an error if this method does not exist
        assert (
            stage.capitalize() == stage.name.capitalize()
        )  # Ensure the capitalize function is working as expected


def test_fcc_Stages__get_steering_script_names_for_all_ordered_combinations_of_stages(
    mocker, ordered_permutations
):
    """Test the _get_steering_script_names function for all possible ordered combinations of stages
    i.e stage1, stage2 or stage1, stage2, final, plot etc."""
    # Loop through each permutation testing the _get_steering_script_names function
    for active_stages in ordered_permutations:
        mock_stage_scripts = [
            Path(f"{stage.name}_flavour.py") for stage in active_stages
        ]
        mock_glob = mocker.patch.object(Path, "glob", return_value=mock_stage_scripts)

        result = Stages._get_steering_script_names()
        # The return value should be the stems, i.e stage1_flavour.py returns stage1
        assert result == [p.stem for p in mock_stage_scripts]
        mock_glob.assert_called_once_with("*.py")


def test_fcc_Stages__get_active_stages_for_all_ordered_combinations_of_stages(
    mocker, ordered_permutations
):
    """Test the _get_active_stages function for all possible ordered combinations of stages
    i.e stage1, stage2 or stage1, stage2, final, plot etc."""
    # Loop through each permutation testing the _get_steering_script_names function
    for active_stages in ordered_permutations:
        mock_stage_names = [stage.name for stage in active_stages]
        mock_get_steering_script_names = mocker.patch.object(
            Stages, "_get_steering_script_names", return_value=mock_stage_names
        )

        result = Stages._get_active_stages()
        # The return value should be the variants of the Stages enum, i.e Stages.stage1
        assert result == [
            Stages[s] for s in mock_stage_names
        ]  # The return value should be the stems, i.e stage1_flavour.py returns stage1
        assert mock_get_steering_script_names.call_count == 1


def test_fcc_Stages_check_for_unregistered_stage_file_False_for_all_ordered_combinations_of_stages(
    mocker, ordered_permutations
):
    """Test the check_for_unregistered_stage_file function for all possible ordered combinations of stages
    i.e stage1, stage2 or stage1, stage2, final, plot etc."""
    for active_stages in ordered_permutations:
        mock_steering_scripts = [Path(f"{s.name}_flavour.py") for s in active_stages]

        mock_get_steering_script_names = mocker.patch.object(
            Stages, "_get_steering_script_names", return_value=mock_steering_scripts
        )
        mock_get_active_stages = mocker.patch.object(
            Stages, "_get_active_stages", return_value=active_stages
        )

        result = Stages.check_for_unregistered_stage_file()

        assert not result
        assert mock_get_active_stages.call_count == 1
        assert mock_get_steering_script_names.call_count == 1


def test_fcc_Stages_check_for_unregistered_stage_file_True_for_all_ordered_combinations_of_stages(
    mocker,
):
    """Test the check_for_unregistered_stage_file function for unregistered file"""

    # Make there be one less script than active stages
    mock_steering_scripts = [Path(f"{s.name}_flavour.py") for s in list(Stages)[:-1]]

    mock_get_steering_script_names = mocker.patch.object(
        Stages, "_get_steering_script_names", return_value=mock_steering_scripts
    )
    mock_get_active_stages = mocker.patch.object(
        Stages, "_get_active_stages", return_value=list(Stages)
    )

    result = Stages.check_for_unregistered_stage_file()

    assert result
    assert mock_get_active_stages.call_count == 1
    assert mock_get_steering_script_names.call_count == 1


def test_fcc_get_stage_script_success(mocker):
    """Test the get_stage_script for success"""
    stage1 = list(Stages)[0]
    mock_stage_file = f"{stage1.name}_test.py"
    mock_glob = mocker.patch.object(Path, "glob", return_value=[mock_stage_file])

    result = Stages.get_stage_script(stage1)

    assert result == mock_stage_file
    assert mock_glob.called_once_with(f"{stage1.name}*.py")


def test_fcc_get_stage_script_raises_AssertionError_for_incorrect_stage_type():
    """Test the get_stage_script for AssertionError for incorrect stage"""

    with pytest.raises(AssertionError):
        _ = Stages.get_stage_script("mock")


def test_fcc_get_stage_script_raises_FileNotFoundError_for_unfound_file(mocker):
    """Test the get_stage_script for FileNotFoundError for unfound file"""
    stage1 = list(Stages)[0]
    # We mock the glob output to return nothing simulating the instance where
    # The glob function does not find a file
    mock_glob = mocker.patch.object(Path, "glob", return_value=[])

    with pytest.raises(FileNotFoundError):
        _ = Stages.get_stage_script(stage1)
        assert mock_glob.called_once_with(f"{stage1.name}*.py")


def test_fcc_get_stage_script_raises_RunTimeErrorfor_unfound_file(mocker):
    """Test the get_stage_script for RunTimeError for multiple found files"""
    stage1 = list(Stages)[0]
    mock_stage_files = [f"{stage1.name}_mock.py", f"{stage1.name}_test.py"]
    mock_glob = mocker.patch.object(Path, "glob", return_value=mock_stage_files)

    with pytest.raises(RuntimeError):
        _ = Stages.get_stage_script(stage1)
        assert mock_glob.called_once_with(f"{stage1.name}*.py")


def test_fcc_get_stage_ordering_all_ordered_permutations(mocker, ordered_permutations):
    """Test that get_stage_ordering works for all possible ordered permutations"""
    active_stages_steering_scripts = [
        [f"{stage.name}_flavour" for stage in active_stages]
        for active_stages in ordered_permutations
    ]
    mock_get_steering_script_names = mocker.patch.object(
        Stages, "_get_steering_script_names", side_effect=active_stages_steering_scripts
    )

    for active_stages in ordered_permutations:
        Stages.get_stage_ordering.cache_clear()
        result = Stages.get_stage_ordering()
        assert result == active_stages

    assert mock_get_steering_script_names.call_count == len(ordered_permutations)
