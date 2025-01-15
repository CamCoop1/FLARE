import b2luigi as luigi

from analysis.utils.dirs import find_file
from analysis.utils.jinja2_utils import get_template
from analysis.utils.stages import Stages, get_stage_script


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
        try:
            print(self.get_input_file_names().values())
            (file_path,) = self.get_input_file_names().values()
        except ValueError as e:
            raise RuntimeError("More than one input directory") from e
        return file_path[0]

    @property
    def outputDir_path(self):
        return self.get_output_file_name(f"{self.stage.name}.root")

    @property
    def rendered_template_path(self):
        output_dir = find_file(self.outputDir_path).parent

        return find_file(output_dir, f"steering_{self.stage.name}.py")

    def run_templating(self):
        with get_stage_script(self.stage).open("r") as f:
            python_code = f.read()

        assert (
            "outputDir" not in python_code
        ), f"Please do not define your own output directory in your {self.stage} script. Remove this and rerun"
        assert (
            "inputDir" not in python_code
        ), f"Please do not define your own input directory in your {self.stage} script. Remove this and rerun"

        rendered_tex = self.template.render(
            outputDir=self.outputDir_path,
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
        ), f"Please do not define your own output directory in your {self.stage} script. Remove this and rerun"
        # assert "inputDir" not in python_code, f"Please do not define your own input directory in your {self.stage} script. Remove this and rerun"

        rendered_tex = self.template.render(
            outputDir=self.outputDir_path,
            inputDir="whatever_you_need_it_to_bee",
            python_code=python_code,
        )

        with self.rendered_template_path.open("w") as f:
            f.write(rendered_tex)


class FCCAnalysisRunnerBaseClass(TemplateMethodMixin, luigi.Task):

    stage: Stages
    cmd = ["fccanalysis", "run"]

    def run_fcc_analysis_stage(self):
        # TODO Complete the run method for the generic fcc analysis
        ...

    def run(self):
        if self.requires():
            self.run_templating()
        else:
            self.run_templating_without_requires()
        self.run_fcc_analysis_stage()

    def output(self):
        yield self.add_to_output(f"{self.stage.name}.root")
