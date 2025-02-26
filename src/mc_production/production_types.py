from enum import Enum
from functools import lru_cache
from pathlib import Path

from src.utils.yaml import get_config

class BracketMappings:
    """ 
    This class is a way to centralise the bracket mappings used inside production_types.yaml. 
    
    The idea being that if in the future the brackets change OR new ones are added then this central
    class is where the change is made and everything else will continue. 
    
    Bracket Mapping Types
    ----------------------
    `output` = () 
        Denotes an output file 
    `input` = --
        Denotes an input file from a previous stage in the MC production workflow
    `datatype_parameter` = ++
        Inside the MCProductionBaseClass there exits the datatype parameter. If a given 
        arg requires this specific datatype parameter in its name then it is parsed and added
        during runtime 
    `free_name` = <>
        Denotes where the analyst can take liberties with their naming convention
        
    Methods
    ---------
    `determine_bracket_mapping`: 
        This method takes an argument from the production_types.yaml and checks if there is
        an associated mapping inside this class
    """
    output = '()'
    input = "--"
    datatype_parameter = "++"
    free_name = '<>'
    
    @staticmethod
    def determine_bracket_mapping(arg:str) -> str | None:
        """ 
        Given a arg (type string) this method will check all attributes of the class
        in an attempt to match the arg with one of the attributes. 
        
        Returns:
            value : str
                The matched string
            None: 
                if no attribute is matched
        """
        for name, value in BracketMappings.__dict__.items():
            try:
                if "__" not in name and value in arg:  # Ignore special attributes
                    return value
            except TypeError:               
                continue             
        return None
    
def _strip(arg, mapping: BracketMappings):
    """ 
    This method does nothing more than strip the free name 
    brackets from the argument        
    """
    return arg.replace(mapping[0], "").replace(mapping[1], "")


def check_if_path_matches_mapping(arg : str, path : str | Path, mapping : str) -> bool:
    """ 
    This function returns True if an argument matches a path
    
    Returns False when there is an argument that does not have a matching path
    """
    args = _strip(arg, mapping).split("_")
    return all([(arg in str(path)) for arg in args])

def get_suffix_from_arg(arg) -> str:
    """ 
    For a given arg, get the suffix
    """
    return str(Path(arg).suffix)


@lru_cache
def get_mc_production_types():
    """ 
    This function creates and returns an Enum of all the production types inside 
    the src/mc_production/production_types.yaml
    """
    return Enum(
        'ProductionTypes',
         get_config('production_types', dir='src/mc_production')
    )
