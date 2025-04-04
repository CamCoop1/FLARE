import logging
import shutil
import subprocess

import b2luigi as luigi

from flare.src.fcc_analysis.fcc_inputfiles_mixin import FCCInputFilesMixin
from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.utils.bracket_mappings import BracketMappingCMDBuilderMixin
from flare.src.utils.dirs import find_file
from flare.src.utils.jinja2_utils import get_template

logger = logging.getLogger("luigi-interface")


class FCCTemplateMethodMixin:
    """
    This mixin class gives the inheriting b2luigi task access to the `run_templating` method.
    The idea behind this class is to allow for a generic class that handles creating templates for each
    stage of the analysis with the correct input and output directories
    """

    stage: Stages

    @property
    def output_dir(self):
        """
        The directory where this stages outputs will be located. Must be implemented by the child class
        """
        raise NotImplementedError

    def get_input_file_names(self) -> dict:
        """
        This is a method defined by b2luigi.Task or b2luigi.DispatchableTask
        """
        raise NotImplementedError

    @property
    def template(self):
        """
        Get the FCC Stage template
        """
        return get_template("steering_file.jinja2")

    @property
    def inputDir_path(self):
        """
        Using b2luigi's get_input_file_names get the input directory containing the data for this stage
        """
        file_path_list = next(iter(self.get_input_file_names().values()))
        file_path = find_file(file_path_list[0])

        if file_path.is_file():
            return str(file_path.parent)

        return str(file_path)

    @property
    def rendered_template_path(self):
        """
        The path where the rendered template for this stage that b2luigi will use at run time
        """
        output_dir = find_file(self.output_dir)
        return find_file(output_dir, f"steering_{self.stage.name}.py")

    def run_templating(self):
        """
        Run templating for this stage. Will check:

        Errors
        -------
        - `AssertionError`: if an outputDir is defined in any of the stage scripts
        - `AssertionError`: if an inputDir is defined in any scripts except stage1 IF stage1 does not require another task to complete

        If both assertions are passed, the stage template is rendered and saved to the output directory of this stage
        """
        # Get stage script from Stages enum
        stage_script_path = Stages.get_stage_script(self.stage)
        # Load the python script as text
        with stage_script_path.open("r") as f:
            python_code = f.read()
        # Check for plot stage as its outputdir is defined differently (for no good reason?)

        outputdir_element = "outputDir" if self.stage != Stages.plot else "outdir"

        # Check no outputDir is defined by the user
        assert (
            outputdir_element not in python_code
        ), f"Please do not define your own output directory in your {self.stage} script. Remove this and rerun"

        # If this stage has the default requires, then just copy the script and return early
        if not [s for s in self.requires()]:
            # Check no inputDir is defined by the user
            assert (
                "inputDir" in python_code
            ), f"Please define your own input directory in your {self.stage} script as the input data is required to stage the workflow"
            shutil.copy2(stage_script_path, self.rendered_template_path)
            return
        # Check no inputDir is defined by the user
        assert (
            "inputDir" not in python_code
        ), f"Please do not define your own input directory in your {self.stage} script. Remove this and rerun"

        # Otherwise we must add the inputDir from the required function to the python script
        rendered_tex = self.template.render(
            outputdir_string=outputdir_element,
            outputDir=self.output_dir,
            inputDir=self.inputDir_path,
            python_code=python_code,
        )

        with self.rendered_template_path.open("w") as f:
            f.write(rendered_tex)


class FCCAnalysisBaseClass(
    luigi.DispatchableTask,
    FCCTemplateMethodMixin,
    BracketMappingCMDBuilderMixin,
    FCCInputFilesMixin,
):
    """
    This is the base class inherited by all FCC Stage b2luigi tasks.

    Attributes
    ----------
    `stage` : Stages
        This attribute is a variant of the Stages enum
    """

    stage: Stages

    @property
    def stage_dict(self):
        """
        The dictionary of information for this stage
        """
        return Stages(self.stage).value

    @property
    def prod_cmd(self):
        """
        The cmd for this stage of the FCC Analysis as defined inside
        the fcc_production.yaml
        """
        return self.stage_dict["cmd"].format(*self.collect_cmd_inputs())

    @property
    def output_dir_name(self):
        """
        The output file may be dependent on a datatype parameter so must determine if the output
        file name needs to be parsed and transformed or if we can return the unparsed output file name
        """
        return self.stage_dict["output_file"]

    @property
    def output_dir(self):
        return find_file(self.get_output_file_name(self.output_dir_name))

    def get_file_paths(self):
        """
        Required by `BracketMappingCMDBuilderMixin` to use for error handling when a required file
        cannot be matched with a BracketMapping or found in the analysis directory
        """
        yield Stages.get_stage_script(self.stage)

    @property
    def unparsed_args(self):
        return self.stage_dict["args"]

    def bm_free_name(self, *args, **kwargs) -> str:
        """
        This method is required by `BracketMappingCMDBuilderMixin` to use the `BracketMappings` class
        to build the `prod_cmd` for this stage

        Returns
        --------
        template path: The path to the templated FCC stage script
        """
        return self.rendered_template_path

    def run_fcc_analysis_stage(self):
        """
        This process function essentially acts as the `run` function for a dispatchable task.

        Here the function collects the appropriate cmd to be submitted using the information provided from
        production_types.yaml. Then when ran on the batch system of your choosing, the subprocess.check_call
        will run the cmd and make sure it completes. Once this is done, the output path is moved from the
        tmp folder to the correct folder at which point b2luigi flags the job as done
        """

        logger.info(f"Command to be ran \n\n {self.prod_cmd} \n\n")
        # Run any required pre_run methods for this specific stage for this specific prodtype
        self.pre_run()
        # Run the prod cmd
        subprocess.check_call(self.prod_cmd, cwd=self.output_dir, shell=True)
        # Run any required on_completion methods for this specific stage for this specific prodtype
        self.on_completion()

    @luigi.on_temporary_files
    def process(self):
        """
        Process the FCC stage
        """
        # Create out tmp output directory thanks to the @luigi.on_temporary_files decorator
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Run templating, checking if the stage is the first in the workflow
        logger.info(f"Running templating for {self.stage.name}")
        self.run_templating()
        # Run the fccanalysis stage
        logger.info(f"Running anaysis for {self.stage.name}")
        self.run_fcc_analysis_stage()

    def on_completion(self):
        """
        This function is intended to run the required functions to be ran after the main cmd
        for this stage detailed in production_types.yaml
        """
        try:
            func_names = self.stage_dict["on_completion"]
        except KeyError:
            return

        for func_name in func_names:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                func()

    def pre_run(self):
        """
        This function is intended to run the required functions to be ran prior to the main cmd
        for this stage detailed in production_types.yaml
        """
        try:
            func_names = self.stage_dict["pre_run"]
        except KeyError:
            return

        for func_name in func_names:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                func()

    def output(self):
        yield self.add_to_output(self.output_dir_name)
