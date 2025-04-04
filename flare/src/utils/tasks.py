import logging
from itertools import pairwise
from typing import Any

import b2luigi as luigi

from flare.src.utils.dirs import find_external_file

logger = logging.getLogger("luigi-interface")


class OutputMixin:
    """
    Mix-in class to set the ``result_dir`` and ``log_dir`` of a task to the task name.
    """

    results_subdir = None

    @property
    def log_dir(self):
        if self.results_subdir is not None:
            return find_external_file(
                "log", self.results_subdir, self.__class__.__name__
            )
        return find_external_file("log", self.__class__.__name__)

    @property
    def result_dir(self):
        if self.results_subdir is not None:
            return find_external_file(
                "data", self.results_subdir, self.__class__.__name__
            )
        return find_external_file("data", self.__class__.__name__)


def _linear_task_workflow_generator(
    stages: list[Any],
    class_name: str,
    base_class: luigi.Task,
    class_attrs: dict[Any, dict[str, Any]] = {},
    inject_stage1_dependency: None | luigi.Task = None,
) -> dict[Any, luigi.Task]:
    """The function will take a list of stage strings, a class name and a luigi.Task base class
    and return a dictionary of uninitialised classes that inherit from `luigi.Task` and the `base_class`.

    Each Task is assigned its `requires` function based on the ordering of the `stages` parameter.
    I.e if `stages = ['stage1', 'stage2'] then the luigi Task for stage2 will require the luigi
    Task for stage1

    class_attrs can be passed if certain Stage Task require unique class attributes.
    inject_stage1_dependency can be passed to set the stage one task to require that dependency

    Parameters
    -----------
    `stages` : list[Any]
        The stages list is used to create unique luigi.Task classes and keep the ordering
        set out by this variable. The list can be anything, likely an enum or string but
        what is passed into it will be preserved as the keys of the output dictionary
    `class_name` : str
        The base name used when creating the class. The created class will have name f'{class_name}{stage.capitalise()}'
    `base_class` : luigi.Task
        The base class must be a child of luigi.Task. The base class is intended to be an interface that exploits the symmetries
        of a given production workflow. For example, FCC Analysis tools always has its cmd executables beginning with 'fccanalysis'
    `class_attrs` : dict[Any, dict[str,Any]] | None = None
        The class_attrs are passed if some stage tasks require unique attributes compared to the rest. For example, the FCCAnalysisRunnerBaseClass
        sets the `fcc_cmd = ['fccanalysis', 'run']` This changes for the `final` and `plot` stage, so this can be passed to the `class_attrs`
    `inject_stage1_dependency` : None | luigi.Task = None
        The `inject_stage1_dependency` is a way to make the first stage luigi Task created from the ordered `stages` list to require another luigi Task

    Returns
    ---------
    `tasks` : dict[Any, luigi.Task]
        The keys of this dictionary are the ordered elements of `stages` and the values are the associated luigi Task.

    Note
    ------
    The returned Tasks are **NOT** initialised. What is essentially happening is we are declaring a class as you would normally eg:

    ```
    # Standard class declaration
    class Foo:
        bar = 'hello world'

    # Functional class declaration
    Foo = type(
        'Foo',                   # Name of class
        (),                      # Parent classes
        {'bar' : 'hello world'}  # Attributes
    )
    ```
    The goal of this function is to easily create a linear workflow of any size given the basic parameters.
    """
    assert issubclass(
        base_class, luigi.Task
    ), "To use this hyperfunction the base_class must be a subclass of luigi.Task"
    assert isinstance(stages, list) or isinstance(
        stages, dict
    ), "Argument (1), stages, must be a list or a dict"

    def requires_func(task, dependency):
        """
        The generic requires function for stage dependency
        """

        def _requires(stage_task):
            yield stage_task.clone(dependency)

        return _requires(task)

    # initialised a dictionary where we will store the tasks
    tasks = dict()
    for i, stage in enumerate(stages):
        name = f"{class_name}{stage.capitalize()}"  # e.g., "MCProductionStage1"
        subclass_attributes = {
            "stage": stage,
            "results_subdir": luigi.get_setting("results_subdir"),
        }  # Class attributes
        if class_attrs.get(stage, None):
            subclass_attributes.update(class_attrs[stage])

        # Define the class dynamically
        new_class = type(
            name,  # Class name
            (
                OutputMixin,
                base_class,
            ),  # Inherit from MCProductionBaseTask
            subclass_attributes,
        )
        # Check if injected stage1 dependency is required
        if i == 0 and inject_stage1_dependency:
            # Assert the stage1 dependency is a luigi.Task
            assert issubclass(
                inject_stage1_dependency, luigi.Task
            ), "Injected dependency must be a child class of luigi.Task"
            # Check if any attributes have been passes to the class_attrs that need
            # to be added to the inject_stage1_dependency class
            if class_attrs.get("inject_stage1_dependency", None):
                attr_dict = class_attrs.pop("inject_stage1_dependency")
                _assigne_inject_stage1_dependency_attrs(
                    attr_dict, inject_stage1_dependency
                )
            # Create the dependency
            new_class.requires = (
                lambda task=new_class, dep=inject_stage1_dependency: requires_func(
                    task=task, dependency=dep
                )
            )

        tasks.update({stage: new_class})
        logger.debug(f"Created and registered: {name}")

        for upsteam_task, downstream_task in pairwise(tasks.values()):
            downstream_task.requires = (
                lambda task=downstream_task, dep=upsteam_task: requires_func(
                    task=task, dependency=dep
                )
            )
            tasks[downstream_task.stage] = downstream_task

    return tasks


def _assigne_inject_stage1_dependency_attrs(attr_dict, stage1_dependency):
    """Assign the attributes to the stage1 injected dependency"""
    # Loop through attrs and assign to the task
    for attr_name, attr_value in attr_dict.items():
        setattr(stage1_dependency, attr_name, attr_value)
