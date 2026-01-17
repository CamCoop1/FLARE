"""
This modules function is to be an interface between the FCCAnalysisBaseClass and the analysis directory (StudyDir) defined in
analysis/config/details.yaml. Because the FCC workflow can have any combinations of Stages (stage1, stage2, final, plots) we must
first be able to identify what stages are required before creating the b2luigi.
"""

from enum import Enum
from functools import lru_cache
from graphlib import TopologicalSorter
from itertools import pairwise
from pathlib import Path
from typing import Dict

import b2luigi as luigi

from flare.src.pydantic_models.user_config_model import AddStageModel
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
        return ["stage1", "stage2", "final", "plot"]
        # return [
        #     x.stem
        #     for x in luigi.get_setting("studydir").glob("*.py")
        #     if any(s.name in x.stem for s in cls)
        # ]

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

    @classmethod
    def set_new_dag(cls, dag: Dict[str, set]):
        cls._dag = dag
        cls.get_dag_for_stages.cache_clear()

    @classmethod
    @lru_cache
    def get_dag_for_stages(cls) -> Dict[str, set]:
        if hasattr(cls, "_dag"):
            return cls._dag
        dag: Dict[str, set] = {}
        for downstream_task, upstream_task in pairwise(
            reversed([x.name for x in cls._get_active_stages()])
        ):
            dag.update({downstream_task: {upstream_task}})

        ts = TopologicalSorter(dag)
        ts.static_order()
        cls._dag: Dict[str, set] = dag
        return cls._dag


def generate_stages_enum():
    # Get the full available set of FCC Analysis stages
    fcc_analysis_model = get_config("fcc_production.yaml", dir=Path(__file__).parent)[
        "fccanalysis"
    ]
    # Create a preliminary _Stages enum that we can build off of
    preliminary_stages = _Stages("FCCProductionTypes", fcc_analysis_model)
    # Get the DAG graph for this active FCCAnalysis stages required by the user
    preliminary_ordered_dag: Dict[str, set] = preliminary_stages.get_dag_for_stages()
    # Get the user_add_stage dictionary that the user MAY have passed to their
    # Config.yaml file
    user_add_stage: Dict[str, AddStageModel] = luigi.get_setting("user_add_stage", {})

    fcc_analysis_model.update(user_add_stage)

    for stage_name, add_stage_model in user_add_stage.items():
        required_stages = [x.lower() for x in add_stage_model.required_by]
        requires_stage = add_stage_model.requires.lower()
        # Check if this node has a incoming edge
        if requires_stage:
            preliminary_ordered_dag.update({stage_name: {requires_stage}})
        # Check if this node requires outcoming edges
        if required_stages:
            for stage in required_stages:
                try:
                    stage_dependency = preliminary_ordered_dag[stage]
                    if not any(
                        x in stage_dependency for x in fcc_analysis_model.keys()
                    ):
                        raise ValueError(
                            f"The Task {stage} already has a custom user defined requirement of {stage_dependency}. Each Flare Task can only have one required Task."
                        )
                    preliminary_ordered_dag[stage] = {stage_name}

                except KeyError:
                    if stage in fcc_analysis_model.keys():
                        preliminary_ordered_dag[stage] = {stage_name}
                    else:
                        raise KeyError(
                            f"Unknown Task {stage} declared as requiring {stage_name}. Please check your logic is correct and rerun"
                        )

    dag = TopologicalSorter(preliminary_ordered_dag)
    dag.static_order()
    stages_enum = _Stages("FCCAnalysisStages", fcc_analysis_model)
    stages_enum.set_new_dag(preliminary_ordered_dag)
    return stages_enum


Stages = generate_stages_enum()
