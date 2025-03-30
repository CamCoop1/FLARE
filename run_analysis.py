import b2luigi as luigi

from src.fcc_analysis.fcc_stages import Stages
from src.fcc_analysis.tasks import FCCAnalysisWrapper
from src.utils.logo import print_b2luigi_logo

if __name__ == "__main__":
    luigi.set_setting("run_mc_prod", False)
    print_b2luigi_logo()
    if Stages.check_for_unregistered_stage_file():
        raise RuntimeError(
            "There exists unregistered stages in your analysis. Please register them following the README.md"
            " and rerun"
        )

    luigi.process(FCCAnalysisWrapper(), workers=4, batch=True)
