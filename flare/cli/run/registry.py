from flare.cli.auto_importer import auto_import_package
from flare.cli.cli_registry import GroupHooks, register_group
from flare.cli.lint.run_lint_fcc_scripts import run_fcc_linting
from flare.cli.run.utils import build_for_regular_flare_cli, load_settings_into_manager


def _run_hooks(args):
    build_for_regular_flare_cli(args)
    load_settings_into_manager(args)
    if run_fcc_linting(args):
        # If run_fcc_linting returns a truthy object then there are diagnostics
        # which are not suppressed and so we much exit
        exit(1)


# Create "run" group
run_subparsers = register_group(
    name="run", help="Run FLARE workflows", hooks=GroupHooks(post_parse=_run_hooks)
)

auto_import_package("flare.cli.run")
