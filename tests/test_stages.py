import pytest

import src.utils.stages as stages


@pytest.mark.parametrize("stage", ("stage1", "stage2", "final", "plot"))
def test_check_Stages_enum_has_correct_variants(stage):
    """
    This test is to ensure all variants of the Stages enum
    are as required for the framework
    """

    assert stages.Stages[stage]


@pytest.mark.parametrize(
    "stage, error", (["stage1", RuntimeError], ["stage2", FileNotFoundError])
)
def test_get_stage_script_for_Errors(setup_analysis_files_for_Errors, stage, error):
    """
    Test that the `get_stage_script` function raises:
    - RuntimeError if multiple files for one stage exist
    - FileNotFoundError if a stage file is not present
    """
    stages.stages_directory = setup_analysis_files_for_Errors

    with pytest.raises(error):
        stages.get_stage_script(stages.Stages[stage])


def test_get_stage_script_for_correct_operation(
    setup_analysis_for_unregistered_stage_file,
):
    stages.stages_directory = setup_analysis_for_unregistered_stage_file

    stage1_file = stages.stages_directory / "stage1.py"

    assert stages.get_stage_script(stages.Stages["stage1"]) == stage1_file


def test_check_for_unregistered_stage_file(setup_analysis_for_unregistered_stage_file):
    """
    Check that when an unregistered
    """
    stages.stages_directory = setup_analysis_for_unregistered_stage_file

    assert not stages.check_for_unregistered_stage_file()
