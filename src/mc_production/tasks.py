
import b2luigi as luigi


from src import results_subdir 
from src.utils.tasks import OutputMixin
from src.mc_production.production_types import (
    BracketMappings,
    get_mc_production_types, 
    determine_bracket_mapping,
    get_suffix_from_arg,
    check_if_path_matches_mapping
)
from src.utils.dirs import find_file


class MCProductionBaseTask(luigi.DispatchableTask):
    """ 
    This will serve as the first stage of the MC production workflow
    
    """
    _type = luigi.EnumParameter(enum=get_mc_production_types())
    datatype = luigi.Parameter()
    stage : str
    
    @property
    def input_file_path(self):
        return next(iter(self.get_input_file_names().values()))[0]
    
    @property
    def _unparsed_output_file_name(self):
        return self.stage_dict['output_file']
    
    @property 
    def stage_dict(self):
        return self._type.value[self.stage]
    
    @property
    def cmd_prefix(self):
        return self.stage_dict['cmd']
    
    @property 
    def output_file_name(self):
        if determine_bracket_mapping(self._unparsed_output_file_name) == BracketMappings.datatype_parameter:            
            suffix = get_suffix_from_arg(self._unparsed_output_file_name)
            return f"{self.datatype}{suffix}"
        return self._unparsed_output_file_name
    
        
    def collect_cmd_inputs(self) -> list:
        """ 
        Here should be the code required to get the ordered 
        list of inputs for the given MC production type
        
        """
        cmd_inputs = []
        file_paths = [f for f in find_file('analysis', 'mc_production').glob("*")]
        
        for arg in self.stage_dict['args']:
            match determine_bracket_mapping(arg):
                case BracketMappings.output:    
                    output_path = self.get_output_file_name(self.output_file_name)
                    cmd_inputs.append(output_path)
                case BracketMappings.input:
                    cmd_inputs.append(self.input_file_path)
                case BracketMappings.datatype_parameter:                    
                    parsed_arg = arg.replace(BracketMappings.datatype_parameter, self.datatype)
                    file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(arg, f,BracketMappings.datatype_parameter)][0]
                    cmd_inputs.append(parsed_arg)
                case BracketMappings.free_name:
                    file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(arg, f, BracketMappings.free_name)][0]
                    cmd_inputs.append(file_path)
                                                                         
        return cmd_inputs
    
    def process(self):
        ...
        
    def output(self):
        yield self.add_to_output(self.output_file_name)
    


class MCProductionStage1(OutputMixin, MCProductionBaseTask):
    """ 
    This class serves as the first stage of the MC production workflow
    """
    results_subdir = results_subdir
    stage = 'stage1'
    
    
@luigi.requires(MCProductionStage1)
class MCProductionStage2(OutputMixin, MCProductionBaseTask):
    """ 
    This will serve as the second stage of the workflow 
    """
    results_subdir = results_subdir
    stage = 'stage2'
    