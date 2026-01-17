import argparse
import os
import sys
from enum import Enum
from pathlib import Path

import b2luigi as luigi

from flare.cli.flare_logging import logger
from flare.src.pydantic_models import models
from flare.src.utils.yaml import get_config

COMMON_ARGUMENTS = [
    ("--name", {"help": "Name of the study"}),
    ("--version", {"help": "Version of the study"}),
    ("--description", {"help": "Description of the study"}),
    (
        "--study-dir",
        {"help": "Study directory path where the files for production are located"},
    ),
    (
        "--output-dir",
        {
            "help": "The location where the output file will be produced, by default will be the current working directory"
        },
    ),
    ("--config-yaml", {"help": "Path to a YAML config file"}),
    ("--cwd", {"help": argparse.SUPPRESS, "default": Path().cwd()}),
]


def _get_unwanted_cli_arguments():
    return ["command", "subcommand", "func", "prog"]


def get_flare_cwd() -> Path:
    """This function sets an environment variable that is necessary for
    the batch system"""
    if "FLARE_CWD" not in os.environ:
        os.environ["FLARE_CWD"] = str(Path().cwd())
    return Path(os.environ["FLARE_CWD"])


def load_config(
    cwd: Path,
    pydantic_model=None,
    config_path=None,
    user_yaml=False,
):
    """Load configuration from config.yaml (or a discovered yaml file) if it exists."""

    # Set the config yaml path
    config_path = cwd / (f"{config_path}" if config_path else "config.yaml")
    # Have a check such that if the config path given does not end in '.yaml'
    # we instead search that directory for a yaml file
    if config_path.suffix != ".yaml":
        # Get a list of potential configs
        potental_config = list(config_path.glob("*.yaml"))
        # If no yaml files are found raise assertion
        assert (
            len(potental_config) > 0
        ), f"The provided config-path ({config_path}) does not contain a config.yaml file"
        # If more than one yaml file is found, raise assertion
        assert (
            len(potental_config) == 1
        ), f"The provided config-path ({config_path}) has more than one yaml file in it. Please ensure you provide the correct path"
        # If both of these checks pass, set the true config path
        config_path = potental_config[0]

    # Check the config_path exists
    if config_path.exists():
        # Load the config
        unparsed_data = get_config(
            config_path.name, dir=config_path.parent, user_yaml=user_yaml
        )
        parsed_data = (
            pydantic_model(**unparsed_data) if pydantic_model else unparsed_data
        )
        return parsed_data
    return {}


def load_settings_into_manager(args):
    """Load parsed args into settings manager"""
    logger.info("Loading Settings into FLARE")

    cwd = Path.cwd()
    luigi.set_setting("working_dir", cwd)
    logger.info(f"Current Working Directory: {cwd}")

    # Match on config_yaml in args
    config_path = Path.cwd()
    if hasattr(args, "config_yaml"):
        if args.config_yaml:
            config_path = args.config_yaml
    config = load_config(
        cwd=cwd, pydantic_model=models["UserConfigModel"], config_path=config_path
    )
    # Add Default/config.yaml name to the settings
    name = config.name
    # If user has passed name to CLI we update here
    if hasattr(args, "name"):
        if args.name:
            name = args.name
    luigi.set_setting(key="name", value=name)
    logger.info(f"Name: {luigi.get_setting('name')}")

    # Add Default/config.yaml version to the settings
    version = config.version
    # If user has passed version to CLI we update here
    if hasattr(args, "version"):
        if args.version:
            version = args.version
    luigi.set_setting("version", version)
    logger.info(f"Version: {luigi.get_setting('version')}")

    # Add Default/config.yaml description to the settings
    description = config.description
    # If user has passed description to CLI we update here
    if hasattr(args, "description"):
        if args.description:
            description = args.description

    luigi.set_setting("description", description)
    logger.info(f"description: {luigi.get_setting('description')}")

    # Set Default for the study directory to the settings
    study_dir = ""
    # Check if user pass study_dir to CLI
    if hasattr(args, "study_dir"):
        if args.study_dir:
            study_dir = args.study_dir

    luigi.set_setting(
        "studydir",
        ((cwd / study_dir) if study_dir else (cwd / config.studydir)),
    )
    logger.info(f"Study Directory: {luigi.get_setting('studydir')}")

    # At the results_subdir used in the OutputMixin to the settings
    luigi.set_setting(
        "results_subdir",
        Path(luigi.get_setting("name")) / luigi.get_setting("version"),
    )
    output_dir = Path.cwd()
    if hasattr(args, "output_dir"):
        if args.output_dir:
            output_dir = args.output_dir

    luigi.set_setting("outputdir", Path((output_dir or config.outputdir)))
    results_dir = (
        luigi.get_setting("outputdir") / "data" / luigi.get_setting("results_subdir")
    )
    logger.info(f"Results Directory: {results_dir}")

    # Add the dataprod_dir to the settings
    luigi.set_setting("dataprod_dir", luigi.get_setting("studydir") / "mc_production")
    dataprod_dir = luigi.get_setting("dataprod_dir")

    # Add the dataprod config to the settings, we load the config using load_config
    # if the dataprod_dir does not have a yaml file Assertion errors are raised
    mcprod = False
    if hasattr(args, "mcprod"):
        if args.mcprod:
            mcprod = args.mcprod

    luigi.set_setting(
        "dataprod_config",
        (
            load_config(
                cwd, models["UserMCProdConfigModel"], dataprod_dir, user_yaml=True
            )
            if mcprod
            else {}
        ),
    )

    # Set the mcprod
    luigi.set_setting("mcprod", mcprod)
    # Set the add_stages variable for later use
    luigi.set_setting("user_add_stage", config.add_stage)
    # Any remaining configuration is added to the settings manager here i.e setting the batch_system
    for name, value in config.extra_config_settings.items():
        name = name.lower()  # All settings are lower case
        if not luigi.get_setting(name, default=False):
            logger.info(f"{name}: {value}")
            luigi.set_setting(name, value)

    if not luigi.get_setting("batch_system", False):
        logger.warning(
            "No batch_system setting was found inside the config YAML. Defaulting to 'local'. This will mean no batch jobs are submitted, instead your workflow is ran on the current node."
        )
        luigi.set_setting("batch_system", "local")


def build_for_regular_flare_cli(args):
    """Build the executable for the regular flare CLI"""
    additional_args = [
        " ".join(
            f"--{key.replace('_', '-')} {value if not isinstance(value, Enum) else value.name}"
            for key, value in vars(args).items()
            if value and key not in _get_unwanted_cli_arguments()
        )
    ]
    # Set the executable setting to be flare CLI
    luigi.set_setting("executable", sys.orig_argv)
    # Add the flare CLI commandline arguments
    luigi.set_setting("task_cmd_additional_args", additional_args)
    # Set the add_filename_to_cmd to False so executable_wrapper.sh is formatted correctly
    luigi.set_setting("add_filename_to_cmd", False)
