import logging
from pathlib import Path

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


def _class_generator_hyper_function(stages: list[str], class_name: str): ...
