from flare.cli.auto_importer import auto_import_package
from flare.cli.cli_registry import register_group

# Create "run" group
run_subparsers = register_group(
    name="run",
    help="Run FLARE workflows",
)

auto_import_package("flare.cli.run")
