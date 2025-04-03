from b2luigi import process as _process

from flare.cli.utils import (
    build_executable_and_save_to_settings_manager,
    load_settings_into_manager,
)

__all__ = ["process"]


def process(*args, flare_args, **kwargs):
    load_settings_into_manager(flare_args)
    build_executable_and_save_to_settings_manager(flare_args)

    _process(*args, **kwargs)
