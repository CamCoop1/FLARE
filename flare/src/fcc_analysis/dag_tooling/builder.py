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
from flare.src.pydantic_models.user_config_model import AddFlareTask
from flare.src.pydantic_models.utils import FlareTask


def get_task_graph() -> Dag:
    # Get the User Added stages
    user_add_tasks: Dict[str, AddFlareTask] = luigi.get_setting("user_add_stage", {})
    print(user_add_tasks)
    # Get the internal FLARE FCC Production tasks
    internal_tasks: Dict[str, FlareTask] = luigi.get_setting(
        "internal_fcc_analysis_tasks"
    )
    return build_task_graph(internal_tasks=internal_tasks, user_tasks=user_add_tasks)


def build_task_graph(
    internal_tasks: dict[str, FlareTask],
    user_tasks: dict[str, AddFlareTask],
) -> Dag:

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
    for upstream_task, downstream_task in pairwise(discovered_tasks):
        downstream_task_model = active_fcc_analysis_tasks[downstream_task].model_dump()
        downstream_task_model["requires"] = upstream_task
        active_fcc_analysis_tasks[downstream_task] = FlareTask(**downstream_task_model)

    # Build our dictionary of all tasks
    tasks = {**active_fcc_analysis_tasks, **user_tasks}

    # Empty dict that will hold the nodes and edges of our Dag
    edges: dict[str, set[str]] = {}

    for name, stage in tasks.items():
        if stage.requires:
            # Set any requires
            edges.setdefault(name, set()).add(stage.requires)

        if not isinstance(stage, AddFlareTask):
            continue

        for downstream in stage.required_by:
            # Set any downstream tasks that require this one
            edges.setdefault(downstream, set()).add(name)
    return Dag(edges)  # Return a validated Dag
