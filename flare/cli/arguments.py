import argparse
from pathlib import Path

from flare.cli.run_commands import run_analysis, run_mcproduction

__all__ = ["ParserNames", "get_args"]


class ParserNames:
    pure_flare = "pure_flar"
    flare = "flare"


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
            "help": "The location where the output file will be produced, by default will be the current working directory",
            "default": Path().cwd(),
        },
    ),
    ("--config-yaml", {"help": "Path to a YAML config file"}),
]


def add_common_arguments(parser):
    for arg, options in COMMON_ARGUMENTS:
        parser.add_argument(arg, **options)


def get_args():
    """Here we define the arg parser for the pure case in which a user wished to create their own custom flare workflow and
    need to parse the commandline arguments to the prompt. For example, if a user defined a workflow like so:

    ``` python3
    flare.process(
        task_like_elements = MyB2luigiTask(),
        workers=4,
        batch=True,
        ignore

    )
    ```

    ``` console
    $ python3 run_my_custom_workflow.py --config-yaml analysis/config
    ```

    """
    parser = argparse.ArgumentParser(
        prog=ParserNames.pure_flare,
        description="Pure CLI for running custom b2luigi workflow in FLARE",
    )

    add_common_arguments(parser)
    parser.add_argument(
        "--mcprod",
        action="store_true",
        help="If set, also run mcproduction as part of the analysis",
    )

    args = parser.parse_known_args()[0]
    setattr(args, "prog", parser.prog)
    return args


def _get_args_cli():
    """This arg parser function is used in conjunction with the flare CLI tool and is more robust than the
    'pure' flare cli used inside get_args()."""

    parser = argparse.ArgumentParser(
        prog=ParserNames.flare, description="CLI for FLARE Project"
    )

    subparsers = parser.add_subparsers(dest="command")

    # "run" command
    run_parser = subparsers.add_parser("run", help="Run the flare command")
    run_subparsers = run_parser.add_subparsers(dest="subcommand")

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
    analysis_parser.set_defaults(func=run_analysis)

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

    mcprod_parser.set_defaults(func=run_mcproduction)

    args = parser.parse_known_args()[0]
    setattr(args, "prog", parser.prog)
    return args
