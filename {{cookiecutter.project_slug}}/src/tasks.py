import b2luigi as luigi

from src.utils.stages import Stages, get_stage_ordering
from src.utils.tasks import FCCAnalysisRunnerBaseClass, OutputMixin
from src.utils.yaml import get_config
from src.utils.dirs import find_file

details = get_config("details")

results_subdir = f"{details['Name']}/{details['Version']}"


class MCProduction(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    OPTIONAL This task will handle production of MC for FCC analyses
    """

    # TODO might have to overload the run_fcc_analysis function specifically for MC production as the cmd is unique

    stage = Stages.mcproduction
    results_subdir = results_subdir
    cmd = ["DelphesPythia8_EDM4HEP"]


class AnalysisStage1(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    First stage of the analysis.
    """

    stage = Stages.stage1
    results_subdir = results_subdir

    def requires(self):
        """
        This requires function needs to be dynamic such that if the user has not
        defined the optional mcproduction steering script, the `AnalysisStage1` task will
        properly set the b2luigi workflow to not add `MCProduction` to the workflow
        """
        if Stages.mcproduction in get_stage_ordering():
            return MCProduction()
        # If MC Production isn't required then we must return an empty list to tell
        # b2luigi that there are no required tasks.
        return []


class AnalysisStage2(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    OPTIONAL second stage of analysis prior to the `final` stage
    """

    stage = Stages.stage2
    results_subdir = results_subdir

    def requires(self):
        return AnalysisStage1()


class AnalysisFinal(OutputMixin, FCCAnalysisRunnerBaseClass):
    """
    Final stage of analysis production which generates flat ntuples ready for plotting
    """

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
            yield AnalysisStage2()
        else:
            yield AnalysisStage1()


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

        if Stages.final in get_stage_ordering():
            yield AnalysisFinal()
        elif Stages.stage2 in get_stage_ordering():
            yield AnalysisStage2()
        else:
            yield AnalysisStage1()


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
        return {output_key : luigi.LocalTarget(str(output_path))}
        
    def run(self):
        description = details['Description']
        print(description)
        _, output_path = self.get_output_key_path_pair()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        tmp_output_path = output_path.with_suffix(".tmp.md")

        tmp_output_path.touch()
        with tmp_output_path.open("w") as f:
            f.write(description)
            
        tmp_output_path.rename(output_path)

class FCCAnalysisWrapper(luigi.WrapperTask):
    """ 
    Wrapper task that allows for multiple tasks to be ran in parallel
    
    Here be begin the FCC analysis workflow along with generating documentation for this sample set
    using the analysis/config/details.yaml 
    """
    def requires(self):
        yield AnalysisPlot()            
        yield GenerateAnalysisDescription()