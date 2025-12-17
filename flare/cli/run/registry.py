from flare.cli.auto_importer import auto_import_package
from flare.cli.cli_registry import GroupHooks, register_group
from flare.cli.run.utils import build_for_regular_flare_cli, load_settings_into_manager

# from flare.cli.lint.utils import run_linter PLACE HOLDER


def _run_hooks(args):
    build_for_regular_flare_cli(args)
    load_settings_into_manager(args)
    # run_linter


# Create "run" group
run_subparsers = register_group(
    name="run", help="Run FLARE workflows", hooks=GroupHooks(post_parse=_run_hooks)
)

auto_import_package("flare.cli.run")
