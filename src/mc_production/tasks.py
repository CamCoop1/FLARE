import shutil 
import subprocess
import logging
import b2luigi as luigi
from pathlib import Path 
from functools import lru_cache

from src import results_subdir 
from src.utils.tasks import OutputMixin
from src.mc_production.generator_specific_methods import MadgraphMethods
from src.mc_production.production_types import (
    BracketMappings,
    get_mc_production_types,
    get_suffix_from_arg,
    check_if_path_matches_mapping
)
from src.utils.dirs import find_file
from src.utils.yaml import get_config

prod_config = get_config('details.yaml', 'analysis/mc_production')
logger = logging.getLogger("luigi-interface")

@lru_cache
def _create_mc_stage_classes() -> dict:
    """Dynamically create and register MC production task classes.
    
    Returns a dict of tasks 
    """
    prodtype = prod_config['prodtype']
    
    stages = get_config('production_types.yaml', 'src/mc_production')[prodtype]

    tasks = {}
    for stage in stages:
        class_name = f"MCProduction{stage}"  # e.g., "MCProductionStage1"
        
        # Define the class dynamically
        new_class = type(
            class_name,  # Class name
            (OutputMixin,MCProductionBaseTask,),  # Inherit from MCProductionBaseTask
            {"stage": stage,
             "results_subdir" : results_subdir
             }  # Class attributes
        )
        
        tasks.update({stage : new_class})
        logging.debug(f"Created and registered: {class_name}")

    return tasks

def get_last_stage_task():
    return next(reversed(_create_mc_stage_classes().values()))


class MCProductionBaseTask(luigi.DispatchableTask, MadgraphMethods):
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
    def prod_cmd(self):
        """ 
        The cmd for this stage of the MC production as defined inside 
        the production_types.yaml
        """
        return self.stage_dict['cmd'].format(*self.collect_cmd_inputs())
    
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
        logger.info(f'Gathering cmd arguments for cmd')
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
                    try: 
                        file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(parsed_arg, f,BracketMappings.datatype_parameter)][0]
                    except FileNotFoundError:
                        raise FileNotFoundError(
                            f"There is no file associated with {arg} inside analysis/mc_production."
                            " The framework will exit, ensure this file is present and try again."
                        )
                    # We copy this file to the tmp output dir so we have a history of what input files were used
                    self.copy_input_file_to_output_dir(file_path)
                    cmd_inputs.append(file_path)
                    
                case BracketMappings.free_name:
                    # Find the associated file using the check_if_path_matches_mapping function
                    try: 
                        file_path = [str(f) for f in file_paths if check_if_path_matches_mapping(arg, f, BracketMappings.free_name)][0]
                    except FileNotFoundError:
                        raise FileNotFoundError(
                            f"There is no file associated with {arg} inside analysis/mc_production."
                            " The framework will exit, ensure this file is present and try again."
                        )                    
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
    
        
        logger.info(f"Command to be ran \n\n {self.prod_cmd} \n\n")
        
        # Run any required pre_run methods for this specific stage for this specific prodtype
        self.pre_run()
        # Run the cmd in the tmp directory
        subprocess.check_call(self.prod_cmd, cwd=self.tmp_output_parent_dir, shell=True)
        # Run any required on_completion methods for this specific stage for this specific prodtype
        self.on_completion()    
        
        # Get final output dir
        target = self.tmp_output_parent_dir.with_suffix("")
        
        logging.info(f"Moving {self.tmp_output_parent_dir} -> {target}")
        
        # Move the contents of the tmp dir to the output dir. Not we cannot just move the 
        # directory as b2luigi's batch submitter saves the executable_wrapper.sh to the output dir
        shutil.copytree(self.tmp_output_parent_dir, target, dirs_exist_ok=True)
        # Delete output dir 
        shutil.rmtree(self.tmp_output_parent_dir)
        
    def requires(self):
        """ 
        This function dynamically assigns any required functions per the stage heirachy 
        
        stage1 -> stage2 -> stage3
        
        i.e stage3 requires stage2, stage2 requires stage1        
        """
        if '1' in self.stage:
            return []
        required_stage = f'stage{int(self.stage[-1])-1}'
        
        yield self.clone(_create_mc_stage_classes()[required_stage])
    
    
    def on_completion(self):
        """ 
        This function is intended to run the required functions to be ran after the main cmd 
        for this stage detailed in production_types.yaml
        """
        try:
            func_names = self.stage_dict['on_completion']
        except KeyError:
            return 
        
        for func_name in func_names:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                func()
    
    def pre_run(self):
        """ 
        This function is intended to run the required functions to be ran prior to the main cmd
        for this stage detailed in production_types.yaml
        """
        try:
            func_names = self.stage_dict['pre_run']
        except KeyError:
            return 
        
        for func_name in func_names:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                func()
    
    def output(self):
        yield self.add_to_output(self.output_file_name)
    
    
class MCProductionWrapper(OutputMixin, luigi.DispatchableTask):
    """ 
    This task simply compiles the outputs from the required tasks into a single folder.
    
    This is necessary because the FCC analysis tools works by passing the folder and looking for the expected 
    input parameters to the workflow.    
    """
    prodtype = luigi.Parameter()
    results_subdir = results_subdir
    
    @property
    def input_paths(self):
        return [f[0] for f in  self.get_input_file_names().values()]
    
    @luigi.on_temporary_files    
    def process(self):        
        # Copy the file and its metadata (hence copy2) to the output directory
        for input_file in self.input_paths:
            source = Path(input_file)
            target = self.get_output_file_name(source.name)            
            shutil.copy2(source, target)
            
        
    def output(self):
        for input_file in self.input_paths:
            path = Path(input_file)
            yield self.add_to_output(path.name)     
    
    def requires(self):
        for datatype in prod_config['datatype']:
            yield  get_last_stage_task()(
                prodtype=get_mc_production_types()[self.prodtype],
                datatype = datatype
            )   



