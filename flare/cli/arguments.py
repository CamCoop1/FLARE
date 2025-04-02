import argparse
from pathlib import Path

from flare.cli.run_command import run_command


def get_args():
    """Here we define the arguments for the arg parser and return the
    parsed args"""

    def add_common_arguments(parser):
        for arg, options in common_args:
            parser.add_argument(arg, **options)

    parser = argparse.ArgumentParser(prog="flare", description="CLI for FLARE Project")

    subparsers = parser.add_subparsers(dest="command")

    # "run" command
    run_parser = subparsers.add_parser("run", help="Run the flare command")
    run_subparsers = run_parser.add_subparsers(dest="subcommand")
    # Common arguments
    common_args = [
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
                "help": "The location where the output file will be produced, by default will be the current working directory",
                "default": Path().cwd(),
            },
        ),
        ("--config-yaml", {"help": "Path to a YAML config file"}),
    ]

    # "analysis" subcommand
    analysis_parser = run_subparsers.add_parser(
        "analysis", help="Run the FCC analysis workflow"
    )
    add_common_arguments(analysis_parser)
    analysis_parser.add_argument(
        "--mcprod",
        action="store_true",
        help="If set, also run mcproduction as part of the analysis",
    )
    analysis_parser.set_defaults(func=run_command)

    # "mcproduction" subcommand
    mcprod_parser = run_subparsers.add_parser(
        "mcproduction", help="Run the MC Production workflow"
    )
    add_common_arguments(mcprod_parser)
    mcprod_parser.add_argument(
        "--mcprod",
        action="store_true",  # It will be set to True by default when this subcommand is called
        default=True,
        help=argparse.SUPPRESS,  # Hide from the help menu
    )

    mcprod_parser.set_defaults(func=run_command)

    return parser.parse_known_args()[0]
