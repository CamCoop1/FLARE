import shutil 
import subprocess
import logging
import b2luigi as luigi
from pathlib import Path 

from src import results_subdir 
from src.utils.tasks import OutputMixin
from src.mc_production.production_types import (
    BracketMappings,
    get_mc_production_types,
    get_suffix_from_arg,
    check_if_path_matches_mapping
)
from src.utils.dirs import find_file
from src.utils.yaml import get_config


logger = logging.getLogger("luigi-interface")

class MCProductionBaseTask(luigi.DispatchableTask):
    """ 
    This base class is total generalised to be able to run on any N-stage MC production
    workflow.
    """
    prodtype = luigi.EnumParameter(enum=get_mc_production_types())
    datatype = luigi.Parameter()
    stage : str
    results_subdir : str
    batch_system = 'local'

    
    @property
    def input_file_path(self):
        """ 
        This is the path to the input file from a task downstream that has ran previously
        """
        return next(iter(self.get_input_file_names().values()))[0]
    
    @property
    def _unparsed_output_file_name(self):
        """ 
        The raw output file name from the production_types.yaml. This is then checked inside the property
        output_file_name and transformed as required
        """
        return self.stage_dict['output_file']
    
    @property 
    def stage_dict(self):
        """ 
        The dictionary of information for this stage
        """
        return self.prodtype.value[self.stage]
    
    @property
    def prod_cmd_prefix(self):
        """ 
        The cmd for this stage of the MC production as defined inside 
        the production_types.yaml
        """
        return self.stage_dict['cmd']
    
    @property 
    def tmp_output_parent_dir(self):
        """ 
        The tmp output dir where all outputs of this workflow will be kept
        """
        return Path(self.get_output_file_name(self.output_file_name)).parent.with_suffix('.tmp')
    
    @property 
    def output_file_name(self):
        """ 
        The output file may be dependent on a datatype parameter so must determine if the output 
        file name needs to be parsed and transformed or if we can return the unparsed output file name
        """
        if BracketMappings.determine_bracket_mapping(self._unparsed_output_file_name) == BracketMappings.datatype_parameter:            
            suffix = get_suffix_from_arg(self._unparsed_output_file_name)
            return f"{self.datatype}{suffix}"
        return self._unparsed_output_file_name
    
    def copy_input_file_to_output_dir(self, path):
        """ 
        This function serves to copy a file from analysis/mc_production/ to 
        the tmp output dir for historical book keeping
        """
        source  = Path(path)
        self.tmp_output_parent_dir.mkdir(parents=True, exist_ok=True)
        destination = self.tmp_output_parent_dir / source.name
        shutil.copy(source, destination)

        
    def collect_cmd_inputs(self) -> list:
        """ 
        Here should be the code required to get the ordered 
        list of inputs for the given MC production type
        
        We rely on the BracketMappings class to handle transformations
        along with the helper functions inside production_types.py
        
        """
        logger.info(f'Gathering cmd arguments for {self.prod_cmd_prefix} tool')
        cmd_inputs = []
        file_paths = [f for f in find_file('analysis', 'mc_production').glob("*")]
        
        for arg in self.stage_dict['args']:
            # Match the type of argument 
            match BracketMappings.determine_bracket_mapping(arg):
                case BracketMappings.output:                     
                    # Create the path to the tmp dir    
                    output_path = self.tmp_output_parent_dir / self.output_file_name                    
                    cmd_inputs.append(str(output_path))
                    
                case BracketMappings.input:
                    cmd_inputs.append(self.input_file_path)
                    
                case BracketMappings.datatype_parameter:       
                    # Must replace the datatype_parameter mapping to the datatype attribute             
                    parsed_arg = arg.replace(BracketMappings.datatype_parameter, self.datatype)
                    # Find the associated file using the check_if_path_matches_mapping function
                    file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(parsed_arg, f,BracketMappings.datatype_parameter)][0]
                    # We copy this file to the tmp output dir so we have a history of what input files were used
                    self.copy_input_file_to_output_dir(file_path)
                    cmd_inputs.append(file_path)
                    
                case BracketMappings.free_name:
                    # Find the associated file using the check_if_path_matches_mapping function
                    file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(arg, f, BracketMappings.free_name)][0]
                    # We copy this file to the tmp output dir so we have a history of what input files were used
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
        This process function essentially acts as the `run` function for a dispatchable task. 
        
        Here the function collects the appropriate cmd to be submitted using the information provided from 
        production_types.yaml. Then when ran on the batch system of your choosing, the subprocess.check_call
        will run the cmd and make sure it completes. Once this is done, the output path is moved from the
        tmp folder to the correct folder at which point b2luigi flags the job as done 
        """
        # Gather the cmd to be submitted 
        cmd = " ".join([self.prod_cmd_prefix] + self.collect_cmd_inputs())
        
        logger.info(f"Command to be ran \n\n {cmd} \n\n")
        
        # Run the cmd in the tmp directory
        subprocess.check_call(cmd, cwd=self.tmp_output_parent_dir, shell=True)

        target = self.tmp_output_parent_dir.with_suffix("")
        
        logging.info(f"Moving {self.tmp_output_parent_dir} -> {target}")
        
        # Move the contents of the tmp dir to the output dir. Not we cannot just move the 
        # directory as b2luigi's batch submitter saves the executable_wrapper.sh to the output dir
        shutil.copytree(self.tmp_output_parent_dir, target, dirs_exist_ok=True)
        # Delete output dir 
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
    This will serve as the second stage of the MC production workflow 
    """
    results_subdir = results_subdir
    stage = 'stage2'
    
    
class MCProductionWrapper(OutputMixin, luigi.DispatchableTask):
    
    results_subdir = results_subdir
    
    @property
    def mc_production_output_path(self):
        return Path(next(iter(self.get_all_output_file_names()))).parent
    
    @property
    def input_paths(self):
        return [f[0] for f in  self.get_input_file_names().values()]
    
    @luigi.on_temporary_files    
    def process(self):        
        
        for input_file in self.input_paths:
            source = Path(input_file)
            target = self.get_output_file_name(source.name)            
            shutil.copy2(source, target)
            
        
    def output(self):
        for input_file in self.input_paths:
            path = Path(input_file)
            yield self.add_to_output(path.name)     
    
    def requires(self):
        config = get_config('details.yaml', 'analysis/mc_production')
        for datatype in config['datatype']:
            yield  MCProductionStage2(
                prodtype=get_mc_production_types()[config['prodtype']],
                datatype = datatype
            )   


