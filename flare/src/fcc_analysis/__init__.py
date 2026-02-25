from pathlib import Path

import b2luigi as luigi

from flare.src.pydantic_models.production_types_model import FCCProductionModel
from flare.src.utils.yaml import get_config


def define_fcc_settings():
    """
    Here we will define some basic settings for FLARE to access when using the FCC Analysis
    package.
    """

    # Extract the internal FCC Analysis tasks available inside FLARE
    tasks = FCCProductionModel(
        **get_config("fcc_production.yaml", dir=Path(__file__).parent)
    ).fccanalysis.root
    # Add it to our settings database
    luigi.set_setting("internal_fcc_analysis_tasks", tasks)


define_fcc_settings()
