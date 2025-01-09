from enum import Enum, auto


class Stages(Enum):
    """
    This enum will be the interface between analyst steering scripts and the b2luigi workflow

    NOTE that this enum is structured to reflect the order in which tasks should fun, with the first
    variant of the enum being the first task that needs to run and so forth.
    """

    mcproduction = auto()
    stage1 = auto()
    stage2 = auto()
    final = auto()
    plot = auto()
