import json
from functools import lru_cache
from pathlib import Path

import jsonschema
import yaml

from flare.src.utils.dirs import find_file


@lru_cache(typed=True)
def get_config(config_name, dir="analysis/config"):
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

    try:
        schema_path = find_file(contents.pop("$schema"))
        with open(schema_path) as f:
            schema = json.load(f)
        jsonschema.validate(contents, schema)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The dataproduction schema provided in {dir/config_name} is not a valid schema for flare."
            " Ensure the path is set to flare/src/schemas/mc_production_details.json"
        )
    except KeyError:
        pass
    return contents
