from enum import Enum
from functools import lru_cache
from pathlib import Path

from src.utils.yaml import get_config

class BracketMappings:
    output = '()'
    input = "--"
    datatype_parameter = "++"
    free_name = '<>'
    
   
def determine_bracket_mapping(arg):
    for name, value in BracketMappings.__dict__.items():
        try:
            if "__" not in name and value in arg:  # Ignore special attributes
                return value
        except TypeError:               
            raise AttributeError(
                f'No mapping exists that matches this argument {arg}'
            )


def _strip(arg, mapping: BracketMappings):
    """ 
    This method does nothing more than strip the free name 
    brackets from the argument        
    """
    return arg.replace(mapping[0], "").replace(mapping[1], "")


def check_if_path_matches_mapping(arg, path, mapping : BracketMappings):
    args = _strip(arg, mapping).split("_")
    return all([(arg in str(path)) for arg in args])

def get_suffix_from_arg(arg):
    return str(Path(arg).suffix)
        

@lru_cache
def get_mc_production_types():
    return Enum(
        'ProductionTypes',
         get_config('production_types', dir='src/mc_production')
        )

         
    
