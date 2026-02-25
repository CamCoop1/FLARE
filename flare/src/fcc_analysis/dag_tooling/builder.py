"""
Here we will build the Dag object based on the internal Flare Tasks and the
ones requested by the User in the AddTask feature (if they have requested it)
"""

from itertools import pairwise
from typing import Dict

import b2luigi as luigi

from flare.src.fcc_analysis.dag_tooling.dag_model import Dag
from flare.src.fcc_analysis.dag_tooling.discovery import discover_task_scripts
from flare.src.fcc_analysis.dag_tooling.validation import validate_no_overlap
from flare.src.fcc_analysis.task_registry import TaskRegistry
from flare.src.pydantic_models import AddFlareTask, FlareTask


def get_task_graph() -> Dag:
    """
    This returns to the user the Directed Acyclic Graph for their FCC Analysis Workflow
    """
    # Get the User Added stages
    user_add_tasks: Dict[str, AddFlareTask] = luigi.get_setting("user_add_stage", {})
    # Get the internal FLARE FCC Production tasks
    internal_tasks: Dict[str, FlareTask] = luigi.get_setting(
        "internal_fcc_analysis_tasks"
    )
    return build_task_graph(internal_tasks=internal_tasks, user_tasks=user_add_tasks)


def build_task_graph(
    internal_tasks: dict[str, FlareTask],
    user_tasks: dict[str, AddFlareTask],
) -> Dag:
    """
    Arguments
    ==========
    - `internal_tasks` : dict[str, FlareTask] = The internal FCC Analaysis Tasks defined in FLARE
    - `user_tasks` : dict[str, AddFlareTask] = Any user defined Tasks added inside their config.yaml, note it uses the AddFlareTask model which includes a `required_by` field

    Returns
    ========
    `Dag` = The Dag Model defined inside dag_model.py, the central source of truth for the FCC Analysis workflow required by the user

    Notes
    =====

    This function builds the Directed Acyclic Graph that determines the order in which FLARE Tasks should be ran

    In this function we make use of all the functionality defined inside dag_tooling. We
        - `validate_no_overlap` to ensure any user defined Tasks do not have the same identifying name as an internal FLARE task
        - `discover_tasks_scripts` which finds the active FCC Analysis Tasks the user wants to fun from their current working directory
        - The `Dag` Model which builds a DAG from the edges dictionary created in this function.
    """

    # Check if internal_tasks and user_tasks share any values
    validate_no_overlap(
        set(internal_tasks),
        set(user_tasks),
    )
    # Discover the FCC Analysis Tasks declared by the user via their working directory contents
    discovered_tasks = discover_task_scripts()
    # Keep only the Tasks which are discovered in the working directory
    active_fcc_analysis_tasks = {
        x: y for x, y in internal_tasks.items() if x in discovered_tasks
    }
    # We must update the FlareTask models with the correct requires field based on the order of the discovered_task list
    # We go pairwise through the list in with the Nth element is an Upstream Task and the N+1 is the Downstream task that
    # requires N to run before it
    for upstream_task, downstream_task in pairwise(discovered_tasks):
        # Get the model as a dictionary so we can manipulate it
        downstream_task_model = active_fcc_analysis_tasks[downstream_task].model_dump()
        # Update the requires field
        downstream_task_model["requires"] = upstream_task
        # Rebuild our FlareTask model and validate everything is as intended
        active_fcc_analysis_tasks[downstream_task] = AddFlareTask(
            **downstream_task_model
        )

    # Build our dictionary of all tasks
    tasks = {**active_fcc_analysis_tasks, **user_tasks}
    # Register all the Tasks into our TaskRegistry
    TaskRegistry(tasks=tasks)
    # Empty dict that will hold the nodes and edges of our Dag
    edges: dict[str, set[str]] = {}

    for name, stage in tasks.items():
        if stage.requires:
            # Set any requires
            edges.setdefault(name, set()).add(stage.requires)

        if not isinstance(stage, AddFlareTask):
            # If not isinstance(stage, AddFlareTask) then this is a FlareTask which does not
            # have a required_by field, so we can continue to the next iteration
            continue

        for downstream in stage.required_by:
            # Set any downstream tasks that require this one
            edges.setdefault(downstream, set()).add(name)
    return Dag(edges)  # Return a validated Dag
