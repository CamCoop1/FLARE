
import b2luigi as luigi

from src import results_subdir 
from src.utils.tasks import OutputMixin
from src.mc_production.production_types import get_mc_production_types, ProductionTypeBracketMappings
from src.utils.dirs import find_file


class MCProductionBaseTask(luigi.Task):
    """ 
    This will serve as the first stage of the MC production workflow
    
    """
    _type = luigi.EnumParameter(enum=get_mc_production_types())
    stage : str
    
    @property 
    def stage_dict(self):
        return self._type.value[self.stage]
    
    @property
    def cmd_prefix(self):
        return self.stage_dict['cmd']
    
    def collect_cmd_inputs(self) -> list:
        """ 
        Here should be the code required to get the ordered 
        list of inputs for the given MC production type
        
        """
        cmd_inputs = []
        
        for arg in self.stage_dict['args']:
            if ProductionTypeBracketMappings.output in arg:
                cmd_inputs.append(self.get_output_file_name(self.stage_dict['output_file']))
            else:
                # Here we want to get the identifying name and the suffix 
                prefix, suffix = arg.strip(ProductionTypeBracketMappings.free_name).split("_")
                
                
                    
                
        
    
    def run(self):
        ...
        
    def outputs(self):
        ...
    


class MCProductionStage1(OutputMixin, MCProductionBaseTask):
    """ 
    This class serves as the first stage of the MC production workflow
    """
    sample_name = luigi.Parameter()
    results_subdir = results_subdir
    stage = 'stage1'
    
    
@luigi.requires(MCProductionStage1)
class MCProductionStage2(OutputMixin, MCProductionBaseTask):
    """ 
    This will serve as the second stage of the workflow 
    """
    
    sample_name = luigi.Parameter()
    results_subdir = results_subdir
    stage = 'stage2'
    