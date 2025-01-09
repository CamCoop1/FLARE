import b2luigi as luigi

from analysis.utils.dirs import find_file
from analysis.utils.stages import Stages
from analysis.utils.steering_files import get_stage_steering_script


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


class FCCAnalysisRunnerBaseClass(luigi.Task):

    stage: Stages
    cmd = ["fccanalysis", "run"]

    @property
    def stage_steering_file(self):
        return get_stage_steering_script(self.stage)

    def run(self): ...

    def output(self): ...
