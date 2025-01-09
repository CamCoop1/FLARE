import b2luigi as luigi

from analysis.tasks.analysis_final import AnalysisFinal
from analysis.utils.data import get_data_types


class AnalysisPlot(luigi.Task):
    """
    Plotting stage of analysis using flat ntuple produced by `AnalysisFinal` task
    """

    def run(self): ...

    def output(self): ...

    def requires(self):
        for data_type in get_data_types():
            yield AnalysisFinal(mc_type=data_type)
