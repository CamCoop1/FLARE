import json
import logging
import os
import subprocess

import b2luigi as luigi

from src import dataprod_config, dataprod_dir, flare_config, results_subdir
from src.utils.dirs import find_file
from src.utils.stages import Stages, get_stage_ordering, get_stage_script
from src.utils.tasks import OutputMixin, TemplateMethodMixin
from src.utils.yaml import get_config

logger = logging.getLogger("luigi-interface")


class FCCAnalysisRunnerBaseClass(TemplateMethodMixin, luigi.DispatchableTask):
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
        This is a list comprising of each section of the bash command that must be submitted for a given stage

    """

    stage: Stages
    fcc_cmd = ["fccanalysis", "run"]

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
        self.fcc_cmd.append(str(self.rendered_template_path))
        # Make tmp directory
        os.makedirs(self.outputDir_path_tmp, exist_ok=True)
        # Symlink any needed files in includePaths
        self.symlink_includePaths_in_python_code()

        logger.debug(f"Current working directory {os.getcwd()}")
        # Run the fccanalysis call
        try:
            subprocess.check_call(
                " ".join(self.fcc_cmd), cwd=self.outputDir_path_tmp, shell=True
            )
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
        if [s for s in self.requires()]:
            logger.debug(f"For {self.stage} we are running the regular templating")
            self.run_templating()
        else:
            # First stage of the workflow
            logger.debug(
                f"For {self.stage} we are running the templating without requires"
            )
            self.run_templating_without_requires()
        # Run the fccanalysis command for stage
        logger.info(f"Running anaysis for {self.stage.name}")
        self.run_fcc_analysis_stage()

    def output(self):
        yield self.add_to_output(f"{self.stage.name}_rootfiles")


class AnalysisStage1(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    First stage of the analysis.
    """

    stage = Stages.stage1
    results_subdir = results_subdir

    def requires(self):
        if dataprod_config:
            from src.mc_production.tasks import MCProductionWrapper

            prodtype = get_config(dataprod_config.name, dir=dataprod_dir)["prodtype"]
            yield MCProductionWrapper(prodtype=prodtype)
        else:
            return []


class AnalysisStage2(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    OPTIONAL second stage of analysis prior to the `final` stage
    """

    stage = Stages.stage2
    results_subdir = results_subdir

    def requires(self):
        yield AnalysisStage1()


class AnalysisFinal(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    Final stage of analysis production which generates flat ntuples ready for plotting
    """

    stage = Stages.final
    results_subdir = results_subdir
    fcc_cmd = ["fccanalysis", "final"]

    def requires(self):
        """
        This requires function needs to be dynamic such that if the user has not
        defined the optional stage2 steering script, the `AnalysisFinal` task will
        properly set the b2luigi workflow to go straight to `AnalysisStage1`
        """
        if Stages.stage2 in get_stage_ordering():
            yield AnalysisStage2()
        else:
            yield AnalysisStage1()


class AnalysisPlot(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    Plotting stage of analysis using flat ntuple produced by `AnalysisFinal` task
    """

    stage = Stages.plot
    results_subdir = results_subdir
    fcc_cmd = ["fccanalysis", "plots"]

    def requires(self):
        """
        This sets the workflow of the tasks. We must check firstly if there is a final stage to be ran.

        The full workflow for this framework is

        MC Production -> Stage 1 -> Stage 2 -> Final -> Plots

        If no final stage, then we must check if a stage2 is required.

        Lastly, if neither of these stages are needed we then must jump straight to stage1.
        """

        if Stages.final in get_stage_ordering():
            yield AnalysisFinal()
        elif Stages.stage2 in get_stage_ordering():
            yield AnalysisStage2()
        else:
            yield AnalysisStage1()


class GenerateAnalysisDescription(OutputMixin, luigi.Task):
    """
    This task serves to generate documentation for the current sample set being generated.
    """

    results_subdir = results_subdir

    def get_output_key_path_pair(self):
        output_path = find_file("data", self.results_subdir, "README.md")

        return output_path.name, output_path

    def output(self):
        output_key, output_path = self.get_output_key_path_pair()
        return {output_key: luigi.LocalTarget(str(output_path))}

    def run(self):
        description = flare_config["Description"]
        print(description)
        _, output_path = self.get_output_key_path_pair()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_output_path = output_path.with_suffix(".tmp.md")

        tmp_output_path.touch()
        with tmp_output_path.open("w") as f:
            f.write(description)

        tmp_output_path.rename(output_path)


class FCCAnalysisWrapper(OutputMixin, luigi.WrapperTask):
    """
    Wrapper task that allows for multiple tasks to be ran in parallel

    Here be begin the FCC analysis workflow along with generating documentation for this sample set
    using the analysis/config/details.yaml
    """

    results_subdir = results_subdir

    def requires(self):
        yield AnalysisPlot()
        yield GenerateAnalysisDescription()
