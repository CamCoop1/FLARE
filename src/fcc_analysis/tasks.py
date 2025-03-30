import logging
from functools import lru_cache

import b2luigi as luigi

from src import dataprod_config, flare_config, results_subdir
from src.fcc_analysis.fccanalysis_baseclass import FCCAnalysisRunnerBaseClass
from src.mc_production.tasks import MCProductionWrapper
from src.utils.dirs import find_file
from src.utils.stages import Stages, get_stage_ordering
from src.utils.tasks import OutputMixin, _class_generator_closure_function

logger = logging.getLogger("luigi-interface")

_fcc_stage_tasks_func = _class_generator_closure_function(
    stages=get_stage_ordering(),
    class_name="Analysis",
    base_class=FCCAnalysisRunnerBaseClass,
    class_attrs={
        Stages.final: {"fcc_cmd": ["fccanalysis", "final"]},
        Stages.plot: {"fcc_cmd": ["fccanalysis", "plots"]},
    },
)


@lru_cache
def get_fcc_stages_dict() -> dict:
    if dataprod_config and luigi.get_setting("run_mc_prod", default=False):
        return _fcc_stage_tasks_func(inject_stage1_dependency=MCProductionWrapper)
    return _fcc_stage_tasks_func()


def get_last_task() -> luigi.Task:
    return next(reversed(get_fcc_stages_dict().values()))()


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
        yield get_last_task()
        yield GenerateAnalysisDescription()
