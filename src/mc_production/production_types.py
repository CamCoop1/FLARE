from enum import Enum
from functools import lru_cache

from src import results_subdir 
from src.utils.yaml import get_config

@lru_cache
def get_mc_production_types():
    return Enum(
        'ProductionTypes',
         get_config('production_types', dir='src/mc_production')
        )



