from enum import Enum, auto

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


def check_for_unregistered_stage_file() -> bool:
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
    return stage_steering_file[0]
