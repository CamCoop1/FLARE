import argparse
import os
from pathlib import Path

import yaml

from flare.cli.logging import logger
from flare.flare_settings import settings
from flare.run_analysis import main as analysis_main
from flare.src.utils.yaml import get_config


def get_flare_cwd() -> Path:
    if "FLARE_CWD" not in os.environ:
        os.environ["FLARE_CWD"] = str(Path().cwd())
    return Path(os.environ["FLARE_CWD"])


def load_config(config_path=None):
    """Load configuration from config.yaml if it exists."""

    cwd = get_flare_cwd()
    config_path = cwd / (f"{config_path}" if config_path else "config.yaml")

    if config_path.suffix != ".yaml":
        potental_config = [p for p in config_path.glob("*.yaml")]
        assert (
            len(potental_config) > 0
        ), f"The provided config-path ({config_path}) does not contain a config.yaml file"
        assert (
            len(potental_config) == 1
        ), f"The provided config-path ({config_path}) has more than one yaml file in it. Please ensure you provide the correct path"
        config_path = potental_config[0]

    if config_path.exists():
        with config_path.open("r") as f:
            return yaml.safe_load(f)
    return {}


def run_command(args):
    """Handles the 'run' command."""

    config = load_config(args.config_yaml)
    cwd = get_flare_cwd()

    logger.info("Loading Settings into FLARE")

    settings.set_setting(
        key="name", value=args.name or config.get("Name", "default_name")
    )
    logger.info(f"Name: {settings.get_setting('name')}")

    settings.set_setting("version", args.version or config.get("Version", "1.0"))
    logger.info(f"Version: {settings.get_setting('version')}")

    settings.set_setting(
        "description", args.description or config.get("Description", "No description")
    )
    logger.info(f"description: {settings.get_setting('description')}")

    settings.set_setting(
        "studydir", (cwd / args.study_dir) or (cwd / config.get("StudyDir", cwd))
    )
    logger.info(f"Study Directory: {settings.get_setting('studydir')}")

    settings.set_setting(
        "results_subdir",
        Path(settings.get_setting("name")) / settings.get_setting("version"),
    )
    results_dir = cwd / "data" / settings.get_setting("results_subdir")
    logger.info(f"Results Directory: {results_dir}")

    settings.set_setting(
        "dataprod_dir", settings.get_setting("studydir") / "mc_production"
    )
    dataprod_dir = settings.get_setting("dataprod_dir")
    settings.set_setting(
        "dataprod_config",
        (get_config("details.yaml", dataprod_dir) if dataprod_dir.exists() else None),
    )

    logger.info(settings.get_setting("dataprod_config"))
    # Reconstruct the command
    cmd_string = [
        "flare run analysis "
        + " ".join(
            f"--{key.replace('_', '-')} {value}"
            for key, value in vars(args).items()
            if value and key not in ["command", "analysis", "func"]
        )
    ]

    print(cmd_string)
    analysis_main(executable=cmd_string)


def get_arguments():
    parser = argparse.ArgumentParser(prog="flare", description="CLI for FLARE Project")

    subparsers = parser.add_subparsers(dest="command")

    # "run" command
    run_parser = subparsers.add_parser("run", help="Run the flare command")
    run_parser.add_argument("analysis", help="Run the FCC analysis workflow")
    # run_parser.add_argument("mcproduction", help="Run the MC Production workflow")
    run_parser.add_argument("--name", help="Name of the study")
    run_parser.add_argument("--version", help="Version of the study")
    run_parser.add_argument("--description", help="Description of the study")
    run_parser.add_argument(
        "--study-dir",
        help="Study directory path where the files for production are located",
    )
    run_parser.add_argument(
        "--output-dir",
        help="The location where the output file will be produced, by default will be the current working directory",
        default=Path().cwd(),
    )
    run_parser.add_argument(
        "--config-yaml",
        help=(
            "Path to a YAML config file. If you wish to instead keep the config settings in a yaml file you are parse the location to this function"
            ". Note these settings are by default overridden by arguments passed through the CLI. I.e if you set name='flare' in your config.yaml"
            " but set --name MyProject when running the flare CLI, the MyProject name will take priority."
            " You may also just pass the directory in which your yaml file is located, flare will dynamically find it for you."
        ),
    )
    run_parser.set_defaults(func=run_command)

    set_parser = subparsers.add_parser(
        "set",
        help="Set a setting permanently. Ideal for setting the base_path for data outputs",
    )
    set_parser.add_argument(
        "--base-path",
        help="Set the base path where all outputs and log files will be created",
    )

    return parser.parse_known_args()[0]
