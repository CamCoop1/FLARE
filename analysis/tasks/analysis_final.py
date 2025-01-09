import b2luigi as luigi

from analysis.tasks.analysis_stage2 import AnalysisStage2


class AnalysisFinal(luigi.Task):
    """
    Final stage of analysis production which generates flat ntuples ready for plotting
    """

    mc_type = luigi.EnumParameter()

    def run(self): ...

    def output(self): ...

    def requires(self):
        yield AnalysisStage2(mc_type=self.mc_type)
