"""
This module will hold all the helper functions that are needed to accurately gather a requested steering script for a given stage of the workflow.

For example, is the `AnalysisStage1` task is set to run, we wish to get the analyst steering file for that and to do so we need to search the `stages` directory for the correct one
"""

from analysis.utils.dirs import find_file
from analysis.utils.stages import Stages

stages_directory = find_file("config", "stages")


def check_for_unregistered_steering_file() -> bool:
    """
    This function serves to check if there exits any steering scripts inside the `config/stages` directory that are not
    registered to the Stages enum.

    Returns True if there is an unregistered steering script, otherwise return False
    """
    steering_script_names = [x.stem for x in stages_directory.glob("*.py")]
    # Get all the valid prefixes
    valid_prefixes = [variant.name for variant in Stages]
    # Get a list of files that match the prefixes
    valid_steering_scripts = [
        name
        for prefix in valid_prefixes
        for name in steering_script_names
        if name.startswith(prefix)
    ]
    # Finally, if the two lists aren't the same length then there is an additional unregistered script
    return len(valid_steering_scripts) != len(steering_script_names)


def get_stage_steering_script(stage: Stages):
    """
    Gets the steering file for a given stage
    """
    assert isinstance(
        stage, Stages
    ), "The function get_stage_steering_script takes argument stage which must be of the enum type Stages"

    stage_steering_file = [s for s in stages_directory.glob(f"{stage.name}*.py")]
    if not stage_steering_file:
        # No file was found
        raise FileNotFoundError(
            f"The steering file for stage '{stage.name}' was not found. Please ensure you have prefixed this stages steering file with '{stage.name}' and rerun."
        )
    return stage_steering_file[0]
