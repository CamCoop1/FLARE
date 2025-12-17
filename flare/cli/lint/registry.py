from flare.cli.auto_importer import auto_import_package
from flare.cli.cli_registry import register_group

# Create "run" group
lint_subparsers = register_group(
    name="lint",
    help="Lint one or more FCC analysis scripts to check if they are formatted correctly",
)

auto_import_package("flare.cli.lint")
