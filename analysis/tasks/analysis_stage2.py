import b2luigi as luigi

from analysis.tasks.analysis_stage1 import AnalysisStage1


class AnalysisStage2(luigi.Task):
    """
    OPTIONAL second stage of analysis prior to the `final` stage

    TODO Finish optional stage 2 of analysis
    """

    data_type = luigi.EnumParameter()

    def run(self): ...

    def output(self): ...

    def requires(self):
        yield AnalysisStage1(data_type=self.data_type)
