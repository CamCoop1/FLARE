from enum import Enum
from functools import lru_cache

from src.utils.yaml import get_config


@lru_cache
def get_mc_production_types():
    """
    This function creates and returns an Enum of all the production types inside
    the src/mc_production/production_types.yaml
    """
    return Enum(
        "ProductionTypes", get_config("production_types", dir="src/mc_production")
    )
