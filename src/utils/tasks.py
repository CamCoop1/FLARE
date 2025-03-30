import logging
from itertools import pairwise
from pathlib import Path
from typing import Any

import b2luigi as luigi

from src import results_subdir
from src.utils.dirs import find_file
from src.utils.jinja2_utils import get_template
from src.utils.stages import Stages, get_stage_script

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
        with get_stage_script(self.stage).open("r") as f:
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
        with get_stage_script(self.stage).open("r") as f:
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
    stages: list[str],
    class_name: str,
    base_class: luigi.Task,
    class_attrs: dict[Any, dict[str, Any]] | None = None,
):
    """The closure function will take a list of stage strings, a class name and a luigi.Task base class
    and return a function _create_stage_task_classes. The function that is returned can then be used to
    generate the ordered dict of luigi.Tasks.


    class_attrs can be passed if certain Stage Task require unique class attributes.
    """
    assert issubclass(
        base_class, luigi.Task
    ), "To use this hyperfunction the base_class must be a subclass of luigi.Task"

    def _create_stage_task_classes(
        inject_stage1_dependency: None | luigi.Task = None,
    ) -> dict:
        """Dynamically create and register MC production task classes.

        Returns a dict of tasks
        """

        def requires_func(task, dependency):
            """
            The generic requires function for stage dependency
            """

            def _requires(stage_task):
                yield stage_task.clone(dependency)

            return _requires(task)

        # initialised a dictionary where we will store the tasks
        tasks = {}
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

    return _create_stage_task_classes
