import json
import logging
import shutil

from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.utils.dirs import find_file

logger = logging.getLogger("luigi-interface")


class FCCInputFilesMixin:

    stage: Stages

    @property
    def output_dir(self):
        raise NotImplementedError

    def copy_input_file_to_output_dir(self, source):
        """
        This function serves to copy a file from analysis/mc_productionx/ to
        the tmp output dir for historical book keeping
        """
        source = find_file(source)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        destination = self.output_dir / source.name
        shutil.copy(source, destination)

    def copy_inputfiles_declared_in_stage_script(self):
        """
        Any paths included in the `includePaths` variable of a stage script needs to be
        available inside the output directory at run time for the fccanalysis tool to work. To do this,
        we will copy the files from the analysis area to the output directory prior to running the fccanalysis
        command.

        We also do this for book keeping.

        This function is declared inside the fcc_production.yaml file as a `pre_run` function
        """

        with Stages.get_stage_script(self.stage).open("r") as f:
            python_code = f.read()

        for line in python_code.splitlines():
            if line.startswith("includePaths"):
                unparsed_paths_list = (
                    line.replace("includePaths", "").replace("=", "").strip()
                )
                paths_list = json.loads(unparsed_paths_list)
                for path in paths_list:
                    stages_directory = Stages.get_stage_script(self.stage).parent
                    file_src = f"{stages_directory}/{path}"
                    self.copy_input_file_to_output_dir(file_src)
