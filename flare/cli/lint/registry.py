from flare.cli.auto_importer import auto_import_package
from flare.cli.cli_registry import GroupHooks, register_group
from flare.cli.run.utils import load_settings_into_manager


def _run_hooks(args):
    load_settings_into_manager(args)


# Create "lint" group
lint_subparsers = register_group(
    name="lint",
    help="Entry point for FLAREs linter",
    hooks=GroupHooks(post_parse=_run_hooks),
)

auto_import_package("flare.cli.lint")
