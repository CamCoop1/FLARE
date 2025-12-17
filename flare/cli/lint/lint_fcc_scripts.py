def setup_parser(parser):
    parser.add_argument("--files", help="List of files needed to be linted")
    parser.add_argument("script", help="Python script to lint")
    parser.set_defaults(func=run_fcc_linting)


def run_fcc_linting(args): ...


from flare.cli.lint.registry import lint_subparsers  # noqa

parser = lint_subparsers.add_parser(
    "fccanalysis", help="Lint your FCC Analysis files before running FLARE"
)
setup_parser(parser)
