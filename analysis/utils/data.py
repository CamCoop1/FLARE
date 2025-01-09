from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

from analysis.utils.yaml import get_config


@dataclass
class DataSample:
    """
    TODO This will need to be filled in later once we finalise what our datasample will actually look like

    For now we keep it simple and just have a label
    """

    Label = str


@lru_cache()
def get_data_types():
    """
    Get the data types from the configuration file.

    Returns
    -------
    Enum
        An enum containing the data types from the data configuration file.

    """
    return Enum("DataTypes", list(get_config("data")))
