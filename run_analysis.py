import b2luigi as luigi

from analysis.tasks import AnalysisPlot
from analysis.utils.stages import check_for_unregistered_stage_file

if __name__ == "__main__":
    if check_for_unregistered_stage_file():
        raise RuntimeError(
            "There exists unregistered stages in your analysis. Please register them following the README.md"
            " and rerun"
        )

    luigi.process(AnalysisPlot(), workers=4)
