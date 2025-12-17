import flare
from flare.cli.run.utils import COMMON_ARGUMENTS
from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.fcc_analysis.tasks import FCCAnalysisWrapper


def setup_parser(parser):
    for arg, options in COMMON_ARGUMENTS:
        parser.add_argument(arg, **options)

    parser.add_argument(
        "--mcprod",
        action="store_true",
        help="If set, also run mcproduction as part of the analysis",
    )
    parser.set_defaults(func=run_analysis)


def run_analysis(args):
    """Run the Analysis workflow"""
    if Stages.check_for_unregistered_stage_file():
        raise RuntimeError(
            "There exists unregistered stages in your analysis. Please register them following the README.md"
            " and rerun"
        )

    assert (
        Stages.get_stage_ordering()
    ), "Not FCC Stages have been detected in your study directory"
    flare.process(
        FCCAnalysisWrapper(),
        workers=20,
        batch=True,
        ignore_additional_command_line_args=True,
        flare_args=args,
        from_cli_input=True,
    )


# Registration happens here
from flare.cli.run.registry import run_subparsers  # noqa

parser = run_subparsers.add_parser(
    "analysis",
    help="Run FCC analysis",
)
setup_parser(parser)
