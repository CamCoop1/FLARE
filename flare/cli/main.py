from flare.cli.auto_importer import auto_import_registry
from flare.src.utils.logo import print_flare_logo

auto_import_registry("flare.cli.run")
auto_import_registry("flare.cli.lint")


def main():
    """
    Main entry point for the FLARE CLI, here we will determine what the user is
    wanting to do during this execution.
    """
    # import the get_parser function here to ensure all subcommands are properly registered
    from flare.cli.cli_registry import _GROUP_HOOKS, get_parser

    print_flare_logo()
    # Get the global parser
    parser = get_parser()
    # Split the parsed arguments into known and unknown
    known, remaining = parser.parse_known_args()
    # Get the hooks for the group chosen i.e "run"
    hooks = _GROUP_HOOKS.get(known.group)
    # Run any pre_parse hooks
    if hooks and hooks.pre_parse:
        hooks.pre_parse(known, remaining)
    # Run any post_parse hooks
    if hooks and hooks.post_parse:
        hooks.post_parse(known)
    # Executate attached function

    known.func(known)


if __name__ == "__main__":
    main()
