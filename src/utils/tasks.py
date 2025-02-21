import json
import logging
import os
import subprocess

import b2luigi as luigi

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
            return find_file("analysis", "log", self.results_subdir, self.__class__.__name__)
        return find_file("analysis", "log", self.__class__.__name__)

    @property
    def result_dir(self):
        if self.results_subdir is not None:
            return find_file("analysis", "data", self.results_subdir, self.__class__.__name__)
        return find_file("analysis", "data", self.__class__.__name__)


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
            (file_path,) = self.get_input_file_names().values()
        except ValueError as e:
            raise RuntimeError("More than one input directory") from e
        return file_path[0]

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


class FCCAnalysisRunnerBaseClass(TemplateMethodMixin, luigi.Task):
    """
    This will be the base class for all FCC analysis stages. The idea being that
    you can overload the `cmd` attribute to change the stages.
    For example if you wanted to fun the final stage of the analysis
    you would set

    ```
        cmd = ["fccanalysis", "final"]
    ```

    and the executed command will reflect what the luigi task has set as the `cmd`

    Parameters
    -----------
    `stages` : Stages
        This attribute allows interface with the `Stages` enum

    `cmd` : list
        This is a list comprising of each section of the bash command that must be submited for a given stage

    """

    stage: Stages
    cmd = ["fccanalysis", "run"]

    def symlink_includePaths_in_python_code(self):
        """
        Any paths included in the `includePaths` variable of a stage script needs to be
        available inside the output directory at run time for the fccanalysis tool to work. To do this,
        we will symlink the files from the analysis area to the output directory prior to running the fccanalysis
        command.

        Then upon completion (or failure) the symlinked files will be unlinked leaving the workspace uncluttered
        """
        # This keeps track of symlinked files and by attaching to the class we can access it later
        self.symlinked_scripts = []
        with get_stage_script(self.stage).open("r") as f:
            python_code = f.read()

        file_destination_base = os.path.dirname(self.outputDir_path_tmp)
        for line in python_code.splitlines():
            if line.startswith("includePaths"):
                unparsed_paths_list = (
                    line.replace("includePaths", "").replace("=", "").strip()
                )
                paths_list = json.loads(unparsed_paths_list)
                for path in paths_list:
                    file_destination = f"{file_destination_base}/{path}"
                    logger.info(f"Symlinking {path} to {file_destination}")
                    stages_directory = get_stage_script(self.stage).parent
                    file_src = f"{stages_directory}/{path}"
                    os.symlink(file_src, file_destination, target_is_directory=False)
                    self.symlinked_scripts.append(file_destination)

    def remove_symlink_files(self):
        # Using the symlinked_scripts attribute created in symlink_includePaths_in_python_code
        for path in self.symlinked_scripts:
            if os.path.islink(path):
                os.remove(path)

    def run_fcc_analysis_stage(self):
        """
        This method runs the command defined by `cmd`. The intention being that cmd will be overloaded
        by tasks that have different cmd's, like how the final stage uses `fccanalysis final` as cmd

        Note that the outputDir is initially suffixed by '_tmp' this is to allow the rootfiles to be successfully created.
        Once created, we move the files to the correct outputDir without the '_tmp' at which point
        b2luigi will be told that this task has completed as its output defined in the `output()` method exists.
        """
        # Add the template path to the cmd
        self.cmd.append(str(self.rendered_template_path))
        # Make tmp directory
        os.makedirs(self.outputDir_path_tmp, exist_ok=True)
        # Symlink any needed files in includePaths
        self.symlink_includePaths_in_python_code()

        logger.debug(f"Current working directory {os.getcwd()}")
        # Run the fccanalysis call
        try:
            subprocess.check_call(" ".join(self.cmd), shell=True)
        except subprocess.CalledProcessError as e:
            self.remove_symlink_files()
            raise subprocess.CalledProcessError(
                returncode=e.returncode, cmd=e.cmd, stderr=e.stderr
            )
        # Create the proper output path for b2luigi
        outputDir = self.outputDir_path_tmp.replace("_tmp", "")
        # Rename the tmp directory to the output directory expected by b2luigi
        os.rename(src=self.outputDir_path_tmp, dst=outputDir)
        # Removing symlinked files
        self.remove_symlink_files()

    def run(self):
        # Run templating, checking if the stage is the first in the workflow
        if self.requires():
            self.run_templating()
        else:
            # First stage of the workflow
            self.run_templating_without_requires()
        # Run the fccanalysis command for stage
        logger.info(f"Running anaysis for {self.stage.name}")
        self.run_fcc_analysis_stage()

    def output(self):
        yield self.add_to_output(f"{self.stage.name}_rootfiles")
