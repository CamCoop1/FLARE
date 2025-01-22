from enum import Enum, auto
from functools import lru_cache

from analysis.utils.dirs import find_file

stages_directory = find_file("config", "stages")


class Stages(Enum):
    """
    This enum will be the interface between analyst steering scripts and the b2luigi workflow

    NOTE that this enum is structured to reflect the order in which tasks should fun, with the first
    variant of the enum being the first task that needs to run and so forth. The `auto()` method will automatically
    set the corresponding value to reflect this ordering, 0 through to the final variant.
    """

    mcproduction = auto()  # 0
    stage1 = auto()  # 1
    stage2 = auto()  # 2
    final = auto()  # 3
    plot = auto()  # 4


def _get_steering_script_names():
    """
    Gets the list of steering script names. the idea behind this private function is to ensure that
    whenever one is wanting to get the steering scripts they always use the same `stages_directory`
    """
    return [x.stem for x in stages_directory.glob("*.py")]


def _get_active_stages():
    """
    A private helper function which seeks to factor out the finding of valid steering scripts
    """
    steering_script_names = _get_steering_script_names()
    # Get all the valid prefixes
    valid_prefixes = [variant for variant in Stages]
    # Get a list of files that match the prefixes
    valid_steering_scripts = [
        prefix
        for prefix in valid_prefixes
        for name in steering_script_names
        if name.startswith(prefix.name)
    ]
    return valid_steering_scripts


def check_for_unregistered_stage_file() -> bool:
    """
    This function serves to check if there exits any steering scripts inside the `config/stages` directory that are not
    registered to the Stages enum.

    Returns True if there is an unregistered steering script, otherwise return False
    """
    steering_script_names = _get_steering_script_names()

    valid_steering_scripts = _get_active_stages()
    # Finally, if the two lists aren't the same length then there is an additional unregistered script
    return len(valid_steering_scripts) != len(steering_script_names)


def get_stage_script(stage: Stages):
    """
    Gets the steering file for a given stage
    """
    assert isinstance(
        stage, Stages
    ), "The function get_stage_script takes argument stage which must be of the enum type Stages"

    stage_steering_file = [s for s in stages_directory.glob(f"{stage.name}*.py")]
    if not stage_steering_file:
        # No file was found
        raise FileNotFoundError(
            f"The steering file for stage '{stage.name}' was not found. Please ensure you have prefixed this stages steering file with '{stage.name}' and rerun."
        )
    elif len(stage_steering_file) > 1:
        raise RuntimeError(
            f"The are more than one steering files for {stage.name}. Please ensure there is only one single steering file per stage."
        )
    return stage_steering_file[0]


@lru_cache()
def get_stage_ordering() -> list:
    """
    This function will serve to return a list of the ordering the analyst requires in their fcc analysis.

    For example if inside their analysis they require the stage1, stage2, final and plot stages to run,
    then this function will return an ordered list of `Stages` variants which can be used to align the
    ordering of b2luigi workflow to that which is required by the analyst.
    """
    return _get_active_stages()
