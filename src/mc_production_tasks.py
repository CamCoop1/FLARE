from src.utils.yaml import get_config
from src.utils.tasks import OutputMixin
from src.utils.stages import Stages


details = get_config("details")

results_subdir = f"{details['Name']}/{details['Version']}"


class MCProduction(OutputMixin):
    """
    OPTIONAL This task will handle production of MC for FCC analyses
    """

    # TODO might have to overload the run_fcc_analysis function specifically for MC production as the cmd is unique

    stage = Stages.mcproduction
    results_subdir = results_subdir
    cmd = ["DelphesPythia8_EDM4HEP"]
