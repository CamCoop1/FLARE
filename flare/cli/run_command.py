import os
from pathlib import Path

from flare.cli.logging import logger
from flare.flare_settings import settings
from flare.run_analysis import main as analysis_main
from flare.run_mc_production import main as mc_main
from flare.src.utils.yaml import get_config


def get_flare_cwd() -> Path:
    """This function sets an environment variable that is necessary for
    the batch system"""
    if "FLARE_CWD" not in os.environ:
        os.environ["FLARE_CWD"] = str(Path().cwd())
    return Path(os.environ["FLARE_CWD"])


def load_config(config_path=None):
    """Load configuration from config.yaml if it exists."""
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


def _load_settings_into_manager(args):
    """Load parsed args into settings manager"""
    config = load_config(args.config_yaml)
    cwd = get_flare_cwd()
    logger.info("Loading Settings into FLARE")
    # Add name to the settings
    settings.set_setting(
        key="name", value=args.name or config.get("Name", "default_name")
    )
    logger.info(f"Name: {settings.get_setting('name')}")
    # Add version to the settings
    settings.set_setting("version", args.version or config.get("Version", "1.0"))
    logger.info(f"Version: {settings.get_setting('version')}")
    # Add the description to the settings
    settings.set_setting(
        "description", args.description or config.get("Description", "No description")
    )
    logger.info(f"description: {settings.get_setting('description')}")
    # At the study directory to the settings
    settings.set_setting(
        "studydir", (cwd / args.study_dir) or (cwd / config.get("StudyDir", cwd))
    )
    logger.info(f"Study Directory: {settings.get_setting('studydir')}")
    # At the results_subdir used in the OutputMixin to the settings
    settings.set_setting(
        "results_subdir",
        Path(settings.get_setting("name")) / settings.get_setting("version"),
    )
    results_dir = cwd / "data" / settings.get_setting("results_subdir")
    logger.info(f"Results Directory: {results_dir}")
    # Add the dataprod_dir to the settings
    settings.set_setting(
        "dataprod_dir", settings.get_setting("studydir") / "mc_production"
    )
    dataprod_dir = settings.get_setting("dataprod_dir")
    # Add the dataprod config to the settings, returns None if no config is present
    settings.set_setting(
        "dataprod_config",
        (get_config("details.yaml", dataprod_dir) if dataprod_dir.exists() else None),
    )
    # Set the mcprod
    settings.set_setting("mcprod", args.mcprod)
    logger.debug(settings.get_setting("dataprod_config"))


def _build_executable(args):
    """Build the executable to be passed to b2luigi"""
    # Reconstruct the command for the b2luigi batch submission
    cmd_string = ["flare run"]
    cmd_string += [args.subcommand]
    cmd_string += [
        " ".join(
            f"--{key.replace('_', '-')} {value}"
            for key, value in vars(args).items()
            if value and key not in ["command", "subcommand", "func"]
        )
    ]
    return cmd_string


def run_command(args):
    """Run command for FLARE using CLI inputs"""
    _load_settings_into_manager(args)
    cmd_string = _build_executable(args)

    logger.debug(f"flare cmd: {cmd_string}")
    if args.subcommand == "analysis":
        analysis_main(executable=cmd_string)
    else:
        mc_main(executable=cmd_string)
    logger.info("Flare successfully completed!")
