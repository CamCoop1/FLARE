from b2luigi import get_setting
from b2luigi import process as _process

from flare.cli.utils import (
    build_executable_and_save_to_settings_manager,
    load_settings_into_manager,
)

__all__ = ["process"]


def process(*args, flare_args, **kwargs):
    """
    Here we wrap the b2luigi.process function to handle pre-run things that
    need to be done before the actual b2luigi.process function is called
    """
    load_settings_into_manager(flare_args)
    build_executable_and_save_to_settings_manager(flare_args)

    if not kwargs.get("ignore_additional_command_line_args", None):
        # Always set ignore_additional_command_line_args to True
        kwargs["ignore_additional_command_line_args"] = True

    if not kwargs.get("batch", None):
        # In case the batch_system is set but the batch flag was not set True
        if get_setting("batch_system", default=False):
            kwargs["batch"] = True

    _process(*args, **kwargs)
