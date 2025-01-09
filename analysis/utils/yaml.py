from functools import lru_cache
from pathlib import Path

import yaml as yaml

# import json
# import jsonschema
from analysis.utils.dirs import find_file


@lru_cache(typed=True)
def get_config(config_name, dir="config"):
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

    # TODO Bring back the schema check for each yaml file
    # try:
    #     schema_path = contents.pop("$schema")
    #     with open(find_file(schema_path)) as f:
    #         schema = json.load(f)
    #     jsonschema.validate(contents, schema)
    # except KeyError:
    #     pass

    return contents
