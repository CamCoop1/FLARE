"""
This module will house the validation logic required to assert that
a user is not attempting to use the AddTask feature by overriding an
existing FLARE Task.
"""


def validate_no_overlap(internal: set[str], user: set[str]):
    """
    Given the internal Flare Tasks names set and the ones given by
    the user in AddTask, we will check that there is no overlap in naming
    """
    overlap = internal & user
    if overlap:
        raise ValueError(f"Task names collision: {overlap}")
