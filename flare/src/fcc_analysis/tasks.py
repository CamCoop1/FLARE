import logging
from functools import lru_cache

import b2luigi as luigi

from flare.src.fcc_analysis.fcc_analysis_baseclass import FCCAnalysisBaseClass
from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.mc_production.tasks import MCProductionWrapper
from flare.src.utils.dirs import find_external_file
from flare.src.utils.tasks import OutputMixin, _linear_task_workflow_generator

logger = logging.getLogger("luigi-interface")


@lru_cache
def get_fcc_stages_dict() -> dict:
    """
    Get the ordered dictionary of FCC analysis tasks.

    Parameters
    -----------
    `inject_stage1_dependency`: luigi.Task, default=None
        If the stage1 task of the FCC Analysis needs to require another task, massing a Task to this parameter will set that dependency

    Returns
    --------
    `tasks` : dict[Any, luigi.Task]
        The returned ordered dictionary has keys as per the `stages` list passed to _class_generator_closure_function.
        The values are the associated luigi Tasks that are created as child classes of `FCCAnalysisRunnerBaseClass`

    Note
    -----
    For the FCC Analysis in FLARE, the following configuration is passed to `_class_generator_closure_function`:

    ```
    _linear_task_workflow_generator(
        stages=get_stage_ordering(),
        class_name="Analysis",
        base_class=FCCAnalysisRunnerBaseClass,
        class_attrs={
            Stages.final: {"fcc_cmd": ["fccanalysis", "final"]},
            Stages.plot: {"fcc_cmd": ["fccanalysis", "plots"]},
        },
        inject_stage1_dependency= MCProductionWrapper if dataprod_config and luigi.get_setting("run_mc_prod", default=False) else None
    )
    ```
    """
    return _linear_task_workflow_generator(
        stages=Stages.get_stage_ordering(),
        class_name="Analysis",
        base_class=FCCAnalysisBaseClass,
        inject_stage1_dependency=(
            MCProductionWrapper
            if luigi.get_setting("dataprod_config")
            and luigi.get_setting("mcprod", default=False)
            else None
        ),
        class_attrs=(
            {
                "inject_stage1_dependency": {
                    "prodtype": luigi.get_setting("dataprod_config").get("prodtype")
                }
            }
            if luigi.get_setting("dataprod_config")
            else {}
        ),
    )


def get_last_task() -> luigi.Task:
    """
    Returns the last luigi Task inside `get_mc_prod_stages_dict` and instantiates it
    """
    return next(reversed(get_fcc_stages_dict().values()))()


class GenerateAnalysisDescription(OutputMixin, luigi.Task):
    """
    This task serves to generate documentation for the current sample set being generated.
    """

    @property
    def results_subdir(self):
        return luigi.get_setting("results_subdir")

    def get_output_key_path_pair(self):
        output_path = find_external_file("data", self.results_subdir, "README.md")

        return output_path.name, output_path

    def output(self):
        output_key, output_path = self.get_output_key_path_pair()
        return {output_key: luigi.LocalTarget(str(output_path))}

    def run(self):
        description = luigi.get_setting("description")
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

    @property
    def results_subdir(self):
        return luigi.get_setting("results_subdir")

    def requires(self):
        yield get_last_task()
        yield GenerateAnalysisDescription()
