import os
from pathlib import Path

import b2luigi as luigi

from flare.cli.arguments import ParserNames
from flare.cli.logging import logger
from flare.src.utils.yaml import get_config


def _get_unwanted_cli_arguments():
    return ["command", "subcommand", "func", "prog"]


def get_flare_cwd() -> Path:
    """This function sets an environment variable that is necessary for
    the batch system"""
    if "FLARE_CWD" not in os.environ:
        os.environ["FLARE_CWD"] = str(Path().cwd())
    return Path(os.environ["FLARE_CWD"])


def load_config(config_path=None, expect_dataprod=True):
    """Load configuration from config.yaml (or a discovered yaml file) if it exists."""
    # Get the cwd of the flare user
    cwd = get_flare_cwd()
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
        return get_config(config_path.name, dir=config_path.parent)

    return {}


def load_settings_into_manager(args):
    """Load parsed args into settings manager"""
    config = load_config(args.config_yaml)
    cwd = get_flare_cwd()
    logger.info("Loading Settings into FLARE")
    # Add name to the settings
    luigi.set_setting(key="name", value=args.name or config.get("name", "default_name"))
    logger.info(f"Name: {luigi.get_setting('name')}")
    # Add version to the settings
    luigi.set_setting("version", args.version or config.get("version", "1.0"))
    logger.info(f"Version: {luigi.get_setting('version')}")
    # Add the description to the settings
    luigi.set_setting(
        "description", args.description or config.get("description", "No description")
    )
    logger.info(f"description: {luigi.get_setting('description')}")
    # At the study directory to the settings
    luigi.set_setting(
        "studydir",
        (
            (cwd / args.study_dir)
            if args.study_dir
            else (cwd / config.get("studydir", cwd))
        ),
    )
    logger.info(f"Study Directory: {luigi.get_setting('studydir')}")
    # At the results_subdir used in the OutputMixin to the settings
    luigi.set_setting(
        "results_subdir",
        Path(luigi.get_setting("name")) / luigi.get_setting("version"),
    )
    results_dir = cwd / "data" / luigi.get_setting("results_subdir")
    logger.info(f"Results Directory: {results_dir}")
    # Add the dataprod_dir to the settings
    luigi.set_setting("dataprod_dir", luigi.get_setting("studydir") / "mc_production")
    dataprod_dir = luigi.get_setting("dataprod_dir")
    # Add the dataprod config to the settings, we load the config using load_config
    # if the dataprod_dir does not have a yaml file Assertion errors are raised
    luigi.set_setting(
        "dataprod_config", load_config(dataprod_dir) if args.mcprod else {}
    )
    # Set the mcprod
    luigi.set_setting("mcprod", args.mcprod)
    logger.debug(luigi.get_setting("dataprod_config"))

    # Any remaining configuration is added to the settings manager here i.e setting the batch_system
    for name, value in config.items():
        name = name.lower()  # All settings are lower case
        if not luigi.get_setting(name, default=False):
            luigi.set_setting(name, value)


def build_executable_and_save_to_settings_manager(args):
    """Build the executable to be passed to b2luigi"""
    match args.prog:
        case ParserNames.flare:
            _build_for_regular_flare_cli(args)
        case ParserNames.pure_flare:
            _build_for_pure_flare(args)
        case _:
            raise ValueError(f"This parser is not registered: {args.prog}")


def _build_for_pure_flare(args):
    """Build the executable for the pure CLI"""
    cmd_string = [
        " ".join(
            f"--{key.replace('_', '-')} {value}"
            for key, value in vars(args).items()
            if value and key not in _get_unwanted_cli_arguments()
        )
    ]
    # Add the flare CLI commandline arguments
    luigi.set_setting("task_cmd_additional_args", cmd_string)


def _build_for_regular_flare_cli(args):
    """Build the executable for the regular flare CLI"""
    additional_args = [
        " ".join(
            f"--{key.replace('_', '-')} {value}"
            for key, value in vars(args).items()
            if value and key not in _get_unwanted_cli_arguments()
        )
    ]
    # Set the executable setting to be flare CLI
    luigi.set_setting("executable", ["flare run", args.subcommand])
    # Add the flare CLI commandline arguments
    luigi.set_setting("task_cmd_additional_args", additional_args)
    # Set the add_filename_to_cmd to False so executable_wrapper.sh is formatted correctly
    luigi.set_setting("add_filename_to_cmd", False)
