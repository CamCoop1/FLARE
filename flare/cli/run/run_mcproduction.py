from argparse import SUPPRESS

import b2luigi as luigi

import flare
from flare.cli.run.utils import COMMON_ARGUMENTS
from flare.src.mc_production.tasks import MCProductionWrapper


def setup_parser(parser):
    for arg, options in COMMON_ARGUMENTS:
        parser.add_argument(arg, **options)

    parser.add_argument(
        "--mcprod",
        action="store_true",  # It will be set to True by default when this subcommand is called
        default=True,
        help=SUPPRESS,  # Hide from the help menu
    )
    parser.set_defaults(func=run_mcproduction)


def run_mcproduction(args):
    """Run the MC Production workflow"""
    config = luigi.get_setting("dataprod_config")

    flare.process(
        MCProductionWrapper(prodtype=config["global_prodtype"]),
        workers=20,
        batch=True,
        ignore_additional_command_line_args=True,
        flare_args=args,
        from_cli_input=True,
    )


# Registration happens here
from flare.cli.run.registry import run_subparsers  # noqa

parser = run_subparsers.add_parser(
    "mcproduction",
    help="Run MCProduction workflow",
)
setup_parser(parser)
