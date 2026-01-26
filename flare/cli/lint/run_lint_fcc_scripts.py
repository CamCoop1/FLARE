import argparse
from itertools import chain
from pathlib import Path

import flare
from flare.cli.flare_logging import logger
from flare.cli.lint.src.diagnostics.flare_fcc_diagnostics import (
    ErrorExceptions,
    ErrorLevel,
    generate_flare_diagnostics,
    print_diagnostics,
    print_no_diagnostics_to_show,
)
from flare.cli.lint.src.python_script_analyzer import analyze_python_script


def setup_parser(parser):
    parser.add_argument(
        "--mcprod",
        action="store_true",
        help="If set, also run mcproduction as part of the analysis",
    )
    parser.add_argument("--cwd", default=Path.cwd(), help=argparse.SUPPRESS)
    parser.add_argument(
        "--error-level",
        choices=[e for e in ErrorLevel],
        type=lambda name: ErrorLevel[name],
        default=ErrorLevel.ERROR.name,
        help="Error level of the diagnostics tool",
    )
    parser.set_defaults(func=run_fcc_linting)


def run_fcc_linting(args) -> list:
    from flare.src.fcc_analysis.fcc_stages import Stages

    assert (
        Stages.get_stage_ordering()
    ), "No FCC Stages have been detected in your study directory"
    logger.info("Below is your Workflow to be ran")
    Stages.print_dag()

    paths = [
        str(Stages.get_stage_script(Stages[stage]))
        for stage in Stages.get_stage_ordering()
    ]
    first_stage_error_exceptions = [
        (
            [
                ErrorExceptions.OUTPUTDIR_NOT_REQUIRED,
                ErrorExceptions.INPUTDIR_NOT_REQUIRED,
            ]
            if flare.get_setting("mcprod")
            else [ErrorExceptions.OUTPUTDIR_NOT_REQUIRED]
        )
    ]
    diags = [
        generate_flare_diagnostics(*inputs, error_level=args.error_level)
        for inputs in zip(
            # AnalyzerModels for each script
            map(analyze_python_script, paths),
            # Path of each file
            paths,
            # For Stage1 we ignore only OUTPUTDIR definitions
            first_stage_error_exceptions
            + [
                # For every other stage, FLARE must define all inputDir and
                # outputDir variables
                [
                    ErrorExceptions.INPUTDIR_NOT_REQUIRED,
                    ErrorExceptions.OUTPUTDIR_NOT_REQUIRED,
                ]
            ]
            * (len(paths) - 1),
        )
    ]

    diags = list(chain(*diags))
    non_suppressed_diags = [d for d in diags if not d.suppressed]
    if non_suppressed_diags:
        print_diagnostics(non_suppressed_diags)
    else:
        print_no_diagnostics_to_show()

    return non_suppressed_diags


from flare.cli.lint.registry import lint_subparsers  # noqa

parser = lint_subparsers.add_parser(
    "fccanalysis", help="Lint your FCC Analysis files before running FLARE"
)
setup_parser(parser)
