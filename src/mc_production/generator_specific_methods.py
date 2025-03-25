import shutil
import subprocess
from pathlib import Path


class MadgraphMethods:
    """
    This class contains the methods required to run the madgraph workflow for MC generation.

    These methods match those inside production_types.yaml.

    This class is intended to be inherited by the MCProductionBaseTask. This is to avoid polluting
    the base task with too many methods.

    """

    @property
    def tmp_output_parent_dir(self):
        raise NotImplementedError

    @property
    def input_file_path(self):
        raise NotImplementedError

    def madgraph_move_contents_to_tmp_output(self):
        """
        This method is ran after the mg5_aMC command to allow for the additional step of unzipping the unweighted_events.lhe.gz
        file and output it.

        Note we are specifying absolute paths as to not make a mistake and misplace the output file

        """
        cwd_dirs = self.tmp_output_parent_dir.glob("*")

        not_output_dirs = [f for f in cwd_dirs if f.is_dir()]

        assert (
            len(not_output_dirs) == 1
        ), "More than one output directory was made in madgraph running"

        madgraph_dir = not_output_dirs[0]

        zip_file = Path(madgraph_dir, "Events", "run_01", "unweighted_events.lhe.gz")

        cmd = " ".join(
            [
                "gunzip -c",
                str(zip_file),
                ">",
                f"{str(self.tmp_output_parent_dir)}/{self.output_file_name}",
            ]
        )

        subprocess.check_call(cmd, cwd=self.tmp_output_parent_dir, shell=True)

    def madgraph_copy_lhe_file_to_cwd(self):
        """
        When running DelphesPythia8_EMD4HEP, the output .lhe file from stage 1 must be in the cwd for the process to work.

        This method will copy the file as to keep everything in a single place. This is in opposition to symlinking

        """
        input_file_name = Path(self.input_file_path).name

        shutil.copyfile(
            self.input_file_path, dst=f"{self.tmp_output_parent_dir}/{input_file_name}"
        )
