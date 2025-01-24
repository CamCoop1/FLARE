from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

from src.utils.yaml import get_config


@dataclass
class DataSample:
    """
    TODO This will need to be filled in later once we finalise what our datasample will actually look like

    For now we keep it simple and just have a label
    """

    label: str
    fraction: int
    crossSection: float

    def __post_init__(self):
        if isinstance(self.crossSection, str):
            self.crossSection = eval(self.crossSection)


@lru_cache()
def get_input_data() -> list:
    """
    Reads `data.yaml` and produces an object containing all the information for each
    specified dataset.
    """
    DataConfig = get_config("data")
    datasets = {}

    for label, SampleDict in DataConfig.items():
        SampleDict["label"] = label
        sample = DataSample(**SampleDict)
        datasets[sample.label] = sample

    return datasets


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
