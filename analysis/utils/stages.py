from enum import Enum, auto


class Stages(Enum):
    """
    This enum will be the interface between analyst steering scripts and the b2luigi workflow
    """

    mcproduction = auto()
    stage1 = auto()
    stage2 = auto()
    final = auto()
    plot = auto()
