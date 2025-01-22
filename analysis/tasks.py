import b2luigi as luigi

from analysis.utils.data import get_data_types
from analysis.utils.stages import Stages, get_stage_ordering
from analysis.utils.tasks import FCCAnalysisRunnerBaseClass, OutputMixin

results_subdir = "ntuples"


class MCProduction(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    OPTIONAL This task will handle production of MC for FCC analyses
    """

    # TODO might have to overload the run_fcc_analysis function specifically for MC production as the cmd is unique

    data_type = luigi.EnumParameter(enum=get_data_types())
    stage = Stages.mcproduction
    results_subdir = results_subdir
    cmd = ["DelphesPythia8_EDM4HEP"]


class AnalysisStage1(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    First stage of the analysis.
    """

    data_type = luigi.EnumParameter(enum=get_data_types())
    stage = Stages.stage1
    results_subdir = results_subdir

    def requires(self):
        """
        This requires function needs to be dynamic such that if the user has not
        defined the optional mcproduction steering script, the `AnalysisStage1` task will
        properly set the b2luigi workflow to not add `MCProduction` to the workflow
        """
        if Stages.mcproduction in get_stage_ordering():
            return MCProduction(data_type=self.data_type)
        # If MC Production isn't required then we must return an empty list to tell
        # b2luigi that there are no required tasks.
        return []


class AnalysisStage2(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    OPTIONAL second stage of analysis prior to the `final` stage
    """

    data_type = luigi.EnumParameter(enum=get_data_types())
    stage = Stages.stage2
    results_subdir = results_subdir

    def requires(self):
        return AnalysisStage1(data_type=self.data_type)


class AnalysisFinal(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    Final stage of analysis production which generates flat ntuples ready for plotting
    """

    data_type = luigi.EnumParameter(enum=get_data_types())
    stage = Stages.final
    results_subdir = results_subdir
    cmd = ["fccanalysis", "final"]

    def requires(self):
        """
        This requires function needs to be dynamic such that if the user has not
        defined the optional stage2 steering script, the `AnalysisFinal` task will
        properly set the b2luigi workflow to go straight to `AnalysisStage1`
        """
        if Stages.stage2 in get_stage_ordering():
            yield AnalysisStage2(data_type=self.data_type)
        else:
            yield AnalysisStage1(data_type=self.data_type)


class AnalysisPlot(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    Plotting stage of analysis using flat ntuple produced by `AnalysisFinal` task
    """

    stage = Stages.plot
    results_subdir = results_subdir
    cmd = ["fccanalysis", "plots"]

    def requires(self):
        """
        This sets the workflow of the tasks. We must check firstly if there is a final stage to be ran.

        The full workflow for this framework is

        MC Production -> Stage 1 -> Stage 2 -> Final -> Plots

        If no final stage, then we must check if a stage2 is required.

        Lastly, if neither of these stages are needed we then must jump straight to stage1.
        """
        for data_type in get_data_types():
            if Stages.final in get_stage_ordering():
                yield AnalysisFinal(data_type=data_type)
            elif Stages.stage2 in get_stage_ordering():
                yield AnalysisStage2(data_type=data_type)
            else:
                yield AnalysisStage1(data_type=data_type)
