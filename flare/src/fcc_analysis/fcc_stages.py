"""
This modules function is to be an interface between the FCCAnalysisBaseClass and the analysis directory (StudyDir) defined in
analysis/config/details.yaml. Because the FCC workflow can have any combinations of Stages (stage1, stage2, final, plots) we must
first be able to identify what stages are required before creating the b2luigi.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path

import b2luigi as luigi

from flare.src.utils.yaml import get_config


class _Stages(Enum):
    """
    This enum will be the interface between analyst steering scripts and the b2luigi workflow

    NOTE that this enum is structured to reflect the order in which tasks should fun, with the first
    variant of the enum being the first task that needs to run and so forth. The `auto()` method will automatically
    set the corresponding value to reflect this ordering, 0 through to the final variant.
    """

    def capitalize(self):
        return self.name.capitalize()

    @classmethod
    def _get_steering_script_names(cls):
        """Gets the list of steering script names from the `stages_directory`."""
        return [
            x.stem
            for x in luigi.get_setting("studydir").glob("*.py")
            if any(s.name in x.stem for s in cls)
        ]

    @classmethod
    def _get_active_stages(cls):
        """Finds valid steering scripts that match defined Stages variants."""
        steering_script_names = cls._get_steering_script_names()
        valid_prefixes = list(cls)  # Get all valid enum values
        return [
            prefix
            for prefix in valid_prefixes
            for name in steering_script_names
            if name.startswith(prefix.name)
        ]

    @classmethod
    def check_for_unregistered_stage_file(cls) -> bool:
        """
        Checks if any steering scripts exist in `stages_directory` that are not registered to the Stages enum.
        """
        steering_script_names = cls._get_steering_script_names()
        valid_steering_scripts = cls._get_active_stages()
        return len(valid_steering_scripts) != len(steering_script_names)

    @classmethod
    def get_stage_script(cls, stage):
        """
        Gets the steering file for a given stage.
        """
        assert isinstance(
            stage, cls
        ), f"get_stage_script expects a stage of type {cls.__name__}, got {type(stage).__name__} instead."

        stage_steering_file = list(
            luigi.get_setting("studydir").glob(f"{stage.name}*.py")
        )
        if not stage_steering_file:
            raise FileNotFoundError(
                f"No steering file found for stage '{stage.name}'. Ensure it exists with the correct prefix."
            )
        elif len(stage_steering_file) > 1:
            raise RuntimeError(
                f"Multiple steering files found for {stage.name}. Ensure only one file per stage."
            )
        return stage_steering_file[0]

    @classmethod
    @lru_cache
    def get_stage_ordering(cls):
        """
        Returns a list of `Stages` variants in the order required by the analyst.
        """
        return cls._get_active_stages()


Stages = _Stages(
    "FCCProductionTypes",
    get_config("fcc_production.yaml", dir=Path(__file__).parent)["fccanalysis"],
)
