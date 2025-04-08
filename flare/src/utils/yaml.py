from functools import lru_cache
from pathlib import Path

import yaml

from flare.src.pydantic_models import models
from flare.src.utils.dirs import find_file


@lru_cache(typed=True)
def get_config(config_name, dir="analysis/config", user_yaml=False) -> dict:
    """
    Load config YAML file.

    Validates against a given JSON schema, if a path is given in the key ``$schema``.
    This path is interpreted relative to the project base directory.

    Parameters:
        config_name (str, pathlib.Path): Name of the config file *e.g* 'data' or
            'variables'

    Returns:
        contents (dict): Contents of config YAML file.
    """
    YAMLFile = find_file(dir, Path(config_name).with_suffix(".yaml"))
    with open(YAMLFile) as f:
        contents = yaml.safe_load(f)

    # If no model is provided return early with the contents
    validation_model = contents.pop("$model", None)
    if not validation_model:
        if user_yaml:
            raise ValueError(
                f"Your configuration yaml located at {dir}/{config_name} does not have a validation Model attached."
                f""" Ensure your config yaml has the following defined:

                \033[92m'$model' : UserMCProdConfigModel\033[0m
                ^^^^^^^ Add this ^^^^^^^^^

Once you have added this, please re-run flare.
                """
            )
        else:
            return contents

    try:
        model = models[validation_model]
        validated_model = model(**contents)
    except KeyError:
        raise KeyError(
            f"The model {validation_model} does not exist. The validation models are as show: "
            ", ".join(models.keys())
        )

    return validated_model.dict()
