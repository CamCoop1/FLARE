def setup_parser(parser):
    parser.add_argument("--files", help="List of files needed to be linted")


def run_fcc_linting(args): ...


from flare.cli.lint.registry import lint_subparsers  # noqa

parser = lint_subparsers.add_parser(
    "fccanalysis", help="Lint your FCC Analysis files before running FLARE"
)
