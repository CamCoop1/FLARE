import subprocess
import b2luigi as luigi
import logging

from pathlib import Path 
import shutil 

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


logger = logging.getLogger("luigi-interface")

class MCProductionBaseTask(luigi.DispatchableTask):
    """ 
    This will serve as the first stage of the MC production workflow
    
    """
    prodtype = luigi.EnumParameter(enum=get_mc_production_types())
    datatype = luigi.Parameter()
    stage : str
    results_subdir : str
    batch_system = 'local'

    
    @property
    def input_file_path(self):
        return next(iter(self.get_input_file_names().values()))[0]
    
    @property
    def _unparsed_output_file_name(self):
        return self.stage_dict['output_file']
    
    @property 
    def stage_dict(self):
        return self.prodtype.value[self.stage]
    
    @property
    def prod_cmd_prefix(self):
        return self.stage_dict['cmd']
    
    @property 
    def tmp_output_parent_dir(self):
        return Path(self.get_output_file_name(self.output_file_name)).parent.with_suffix('.tmp')
    
    @property 
    def output_file_name(self):
        if determine_bracket_mapping(self._unparsed_output_file_name) == BracketMappings.datatype_parameter:            
            suffix = get_suffix_from_arg(self._unparsed_output_file_name)
            return f"{self.datatype}{suffix}"
        return self._unparsed_output_file_name
    
    def copy_input_file_to_output_dir(self, path):
        source  = Path(path)
        self.tmp_output_parent_dir.mkdir(parents=True, exist_ok=True)
        destination = self.tmp_output_parent_dir / source.name
        shutil.copy(source, destination)
    
        
    def collect_cmd_inputs(self) -> list:
        """ 
        Here should be the code required to get the ordered 
        list of inputs for the given MC production type
        
        """
        logger.info(f'Gathering cmd arguments for {self.prod_cmd_prefix} tool')
        cmd_inputs = []
        file_paths = [f for f in find_file('analysis', 'mc_production').glob("*")]
        
        for arg in self.stage_dict['args']:
            match determine_bracket_mapping(arg):
                case BracketMappings.output:                        
                    output_path = self.tmp_output_parent_dir / self.output_file_name                    
                    cmd_inputs.append(str(output_path))
                case BracketMappings.input:
                    cmd_inputs.append(self.input_file_path)
                case BracketMappings.datatype_parameter:                    
                    parsed_arg = arg.replace(BracketMappings.datatype_parameter, self.datatype)
                    file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(parsed_arg, f,BracketMappings.datatype_parameter)][0]
                    self.copy_input_file_to_output_dir(file_path)
                    cmd_inputs.append(file_path)
                case BracketMappings.free_name:
                    file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(arg, f, BracketMappings.free_name)][0]
                    self.copy_input_file_to_output_dir(file_path)
                    cmd_inputs.append(file_path)
                case _:
                    raise FileNotFoundError(
                        "There is no file in analysis/mc_production that"
                        f" matches {arg}. Please ensure all files are present for your"
                        f" chosen MC production workflow {self.prodtype.name}"
                    )                                                
        return cmd_inputs
    

    def process(self):
        """ 
        """
        cmd = " ".join([self.prod_cmd_prefix] + self.collect_cmd_inputs())
        
        
        self.tmp_output_parent_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Command to be ran \n\n {cmd} \n\n")
        
        subprocess.check_call(cmd, cwd=self.tmp_output_parent_dir, shell=True)

        target = self.tmp_output_parent_dir.with_suffix("")
        
        logging.info(f"Moving {self.tmp_output_parent_dir} -> {target}")
        shutil.copytree(self.tmp_output_parent_dir, target, dirs_exist_ok=True)
        shutil.rmtree(self.tmp_output_parent_dir)
        
        
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
    
    # def requires(self):
    #     yield self.clone(MCProductionStage1)
    
if __name__ == "__main__":
    luigi.process(MCProductionStage2(
        prodtype=get_mc_production_types()['whizard'],
        datatype = 'wzp6_ee_mumuH_Hbb_ecm240',        
    ))