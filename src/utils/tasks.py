import logging
from itertools import pairwise
from pathlib import Path
from typing import Any

import b2luigi as luigi

from src import results_subdir
from src.utils.dirs import find_file
from src.utils.fcc_stages import Stages
from src.utils.jinja2_utils import get_template

logger = logging.getLogger("luigi-interface")


class OutputMixin:
    """
    Mix-in class to set the ``result_dir`` and ``log_dir`` of a task to the task name.
    """

    results_subdir = None

    @property
    def log_dir(self):
        if self.results_subdir is not None:
            return find_file("log", self.results_subdir, self.__class__.__name__)
        return find_file("log", self.__class__.__name__)

    @property
    def result_dir(self):
        if self.results_subdir is not None:
            return find_file("data", self.results_subdir, self.__class__.__name__)
        return find_file("data", self.__class__.__name__)


class TemplateMethodMixin:
    """
    This mixin class gives the inheriting b2luigi task access to the `run_templating` method.
    The idea behind this class is to allow for a generic class that handles creating templates for each
    stage of the analysis with the correct input and output directories
    """

    stage: Stages

    @property
    def template(self):
        return get_template("steering_file.jinja2")

    @property
    def inputDir_path(self):

        file_path_list = next(iter(self.get_input_file_names().values()))
        file_path = Path(file_path_list[0])

        if file_path.is_file():
            return str(file_path.parent)

        return str(file_path)

    @property
    def outputDir_path_tmp(self):
        """
        Note we make this a tmp directory otherwise b2luigi will flag this as complete before the rootfiles have populated the output directory
        """
        return self.get_output_file_name(f"{self.stage.name}_rootfiles").replace(
            "rootfiles", "rootfiles_tmp"
        )

    @property
    def rendered_template_path(self):
        output_dir = find_file(self.outputDir_path_tmp).parent

        return find_file(output_dir, f"steering_{self.stage.name}.py")

    def run_templating(self):
        with Stages.get_stage_script(self.stage).open("r") as f:
            python_code = f.read()

        if self.stage != Stages.plot:
            outputdir = "outputDir"
        else:
            outputdir = "outdir"

        assert (
            outputdir not in python_code
        ), f"Please do not define your own output directory in your {self.stage} script. Remove this and rerun"

        assert (
            "inputDir" not in python_code
        ), f"Please do not define your own input directory in your {self.stage} script. Remove this and rerun"

        rendered_tex = self.template.render(
            outputdir_string=outputdir,
            outputDir=self.outputDir_path_tmp,
            inputDir=self.inputDir_path,
            python_code=python_code,
        )

        with self.rendered_template_path.open("w") as f:
            f.write(rendered_tex)

    def run_templating_without_requires(self):
        with Stages.get_stage_script(self.stage).open("r") as f:
            python_code = f.read()

        assert (
            "outputDir" not in python_code
        ), f"Please do not define your own output directory in your {self.stage.name} script. Remove this and rerun"

        assert (
            "inputDir" in python_code
        ), f"Please ensure you define the inputDir in the first stage steering script of your analysis, {self.stage.name}."

        rendered_tex = self.template.render(
            outputdir_string="outputDir",
            outputDir=self.outputDir_path_tmp,
            python_code=python_code,
        )

        with self.rendered_template_path.open("w") as f:
            f.write(rendered_tex)


def _class_generator_closure_function(
    stages: list[Any],
    class_name: str,
    base_class: luigi.Task,
    class_attrs: dict[Any, dict[str, Any]] | None = None,
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
            "results_subdir": results_subdir,
        }  # Class attributes
        if class_attrs and class_attrs.get(stage):
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
        if i == 0 and inject_stage1_dependency:
            assert issubclass(
                inject_stage1_dependency, luigi.Task
            ), "Injected dependency must be a child class of luigi.Task"
            new_class.requires = lambda self=new_class: requires_func(
                self, inject_stage1_dependency
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
