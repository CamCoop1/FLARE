import b2luigi as luigi


class AnalysisStage1(luigi.Task):
    """
    First stage of the analysis.
    """

    data_type = luigi.EnumParameter()

    def run(self): ...

    def output(self): ...

    def requires(self): ...
