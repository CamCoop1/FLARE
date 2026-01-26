"""
This modules function is to be an interface between the FCCAnalysisBaseClass and the analysis directory (StudyDir) defined in
analysis/config/details.yaml. Because the FCC workflow can have any combinations of Stages (stage1, stage2, final, plots) we must
first be able to identify what stages are required before creating the b2luigi.
"""

from collections import Counter
from enum import Enum
from functools import lru_cache
from itertools import pairwise
from pathlib import Path
from typing import Dict, Iterable, List

import b2luigi as luigi

from flare.src.pydantic_models.dag_model import Dag
from flare.src.pydantic_models.production_types_model import FCCProductionModel
from flare.src.pydantic_models.user_config_model import AddStageModel
from flare.src.utils.yaml import get_config


class _TaskDeterminationTool(Enum):
    """
    This enum will be the interface between analyst steering scripts and the b2luigi workflow

    NOTE that this enum is structured to reflect the order in which tasks should fun, with the first
    variant of the enum being the first task that needs to run and so forth. The `auto()` method will automatically
    set the corresponding value to reflect this ordering, 0 through to the final variant.
    """

    def capitalize(self):
        return self.name.capitalize()

    @classmethod
    def _get_steering_script_names(cls) -> list[str]:
        """Gets the list of steering script names from the `stages_directory`.

        I.e  return ["stage2", "final", "plot"]"""

        return [
            x.stem
            for x in luigi.get_setting("studydir").glob("*.py")
            if any(s.name in x.stem for s in cls)
        ]

    @classmethod
    def _get_active_stages(cls) -> list[Enum]:
        """Finds valid steering scripts that match defined Enum variants."""
        steering_script_names = cls._get_steering_script_names()
        valid_prefixes_enums = list(cls)
        # Get all valid enum values
        found_enum_variants = [
            prefix_enum
            for prefix_enum in valid_prefixes_enums
            for name in steering_script_names
            if name.startswith(prefix_enum.name)
        ]
        assert len(found_enum_variants) == len(
            steering_script_names
        ), "You have not provided the correct number of steering scripts in your working directory"

        return found_enum_variants

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
        if hasattr(cls, "_dag"):
            return cls._dag.flattened_dag_ordering
        cls.get_dag_for_stages()
        return cls._dag.flattened_dag_ordering

    @classmethod
    def set_new_dag(cls, dag: Dag):
        cls._dag = dag
        cls.get_dag_for_stages.cache_clear()
        cls.get_stage_ordering.cache_clear()

    @classmethod
    @lru_cache
    def get_dag_for_stages(cls) -> Dag:
        if hasattr(cls, "_dag"):
            return cls._dag
        dag: Dict[str, set] = {}
        for downstream_task, upstream_task in pairwise(
            reversed([x.name for x in cls._get_active_stages()])
        ):
            dag.update({downstream_task: {upstream_task}})

        dag_model = Dag(dag)
        cls._dag: Dag = dag_model
        return cls._dag

    @classmethod
    def get_roots_of_dag(cls):
        yield from cls._dag.get_roots_of_dag()

    @classmethod
    def print_dag(cls):
        cls._dag.print_dag()


def _check_no_overlap_between_task_names(*task_names: List[Iterable[str]]):
    """Checks that there are no overlap between internal FLARE task names and the proposed names from
    the users add_stage"""
    flattened_task_names = [
        task_name for internal_list in task_names for task_name in internal_list
    ]

    counter_proposed_task_names = Counter(flattened_task_names)
    double_counted_task_names = [
        x for x, y in counter_proposed_task_names.items() if y > 1
    ]

    assert (
        len(double_counted_task_names) == 0
    ), f"You cannot define a task name to be the same as an internal FLARE task name, problem name is {double_counted_task_names}, {counter_proposed_task_names}"


def _build_dag_for_internal_and_user_tasks(
    preliminary_ordered_dag_model: Dag,
    user_add_stage: Dict[str, AddStageModel],
) -> Dict[str, set[str]]:
    # We want to flatten this DAG into a list of all the stages
    # We have this as a source of truth for ALL the Task names that will
    # be ran
    flattened_dag = preliminary_ordered_dag_model.flattened_dag_ordering
    # We dump the model to a Dict object so we can mutate the data and
    # create a new Dag object later
    preliminary_ordered_dag = preliminary_ordered_dag_model.model_dump()
    # For each add_stage we will build the DAG accordingly
    for stage_name, add_stage_model in user_add_stage.items():
        # Get the required_stages of the
        required_stages = add_stage_model.required_by
        requires_stage = add_stage_model.requires
        # Check if this node has a incoming edge
        if requires_stage:
            preliminary_ordered_dag.update({stage_name: {requires_stage}})
        # Check if this node requires outcoming edges
        if required_stages:
            for stage in required_stages:
                try:
                    # Try pull the stage out of our DAG
                    _ = preliminary_ordered_dag[stage]
                    # If successful update the set value to our stage_name
                    preliminary_ordered_dag[stage] = {stage_name}

                except KeyError:
                    # If we encounter a KeyError we have not found the stage in our DAG
                    # However, this can be the case for our first Task in our DAG, as it will
                    # not have an associated key-value pair designated it has an incoming edge
                    # Hence, we can safely add this stage to our DAG and assign the incoming edge
                    # to be our stage_name
                    if stage in flattened_dag:
                        preliminary_ordered_dag[stage] = {stage_name}
                    else:
                        # If the stage is not in our flattened_dag then we have a KeyError we must deal with
                        raise KeyError(
                            f"Unknown Task {stage} declared as requiring {stage_name}. Please check your logic is correct and rerun"
                            f" If you were expecting that {stage} is apart of the internal FLARE tasks, ensure you have the correct"
                            f" file present in your working directory {stage}_*.py"
                        )

    return (
        preliminary_ordered_dag  # Return the mutated preliminary_ordered_dag variable
    )


@lru_cache
def generate_stages_enum():
    # Get the full available set of FCC Analysis stages
    fcc_analysis_model = FCCProductionModel(
        **get_config("fcc_production.yaml", dir=Path(__file__).parent)
    ).fccanalysis.root
    # Create a preliminary _Stages enum that we can build off of
    preliminary_stages = _TaskDeterminationTool(
        "FCCProductionTypes", fcc_analysis_model
    )
    # # Return early if no studyDir is present i.e tests
    # if not luigi.get_setting("studydir", default=""):
    #     return preliminary_stages
    # Get the DAG graph for this active FCCAnalysis stages required by the user

    preliminary_ordered_dag_model: Dag = preliminary_stages.get_dag_for_stages()
    # Get the user_add_stage dictionary that the user MAY have passed to their
    # Config.yaml file
    user_add_stage: Dict[str, AddStageModel] = luigi.get_setting("user_add_stage", {})
    # Return early if no user_add_stage is present
    if not user_add_stage:
        return preliminary_stages

    # Check that no internal Tasks are in conflict with the users added stage request
    _check_no_overlap_between_task_names(
        fcc_analysis_model.keys(), user_add_stage.keys()
    )

    # After validated, we can add the user_add_stage
    fcc_analysis_model.update(user_add_stage)
    resultant_ordered_dag = _build_dag_for_internal_and_user_tasks(
        preliminary_ordered_dag_model=preliminary_ordered_dag_model,
        user_add_stage=user_add_stage,
    )
    resultant_ordered_dag_model = Dag(resultant_ordered_dag)
    # If we pass, then we can build a new TaskDeterminationTool enum with our updated
    # fcc_analysis_model dictionary
    stages_enum = _TaskDeterminationTool("FCCAnalysisStages", fcc_analysis_model)
    # Set the updated DAG from our _build_dag_for_internal_and_user_tasks function
    stages_enum.set_new_dag(resultant_ordered_dag_model)
    return stages_enum


Stages = generate_stages_enum()
