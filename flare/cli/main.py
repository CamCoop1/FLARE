from flare.cli.arguments import _get_args_cli
from flare.cli.logging import logger
from flare.cli.utils import (
    build_executable_and_save_to_settings_manager,
    load_settings_into_manager,
)
from flare.src.utils.logo import print_b2luigi_logo


def main():
    # Get the commandline arguments
    args = _get_args_cli()
    # Build the executable and save to settings manager
    logger.debug("Building executable from main function")
    build_executable_and_save_to_settings_manager(args)
    # Load the arguments into the luigi settings manager
    logger.debug("Loading settings from main function")
    load_settings_into_manager(args)
    # Check the subparser has a func attribute
    if hasattr(args, "func"):
        # Call the b2luigi logo and run the function
        logger.debug(f"Calling {args.func}")
        print_b2luigi_logo()
        args.func(args)


if __name__ == "__main__":
    main()
