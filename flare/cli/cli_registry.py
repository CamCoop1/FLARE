# flare/cli/cli_registry.py
import argparse

_PARSER = None
_GROUP_SUBPARSERS = None


def get_parser():
    global _PARSER, _GROUP_SUBPARSERS

    if _PARSER is None:
        _PARSER = argparse.ArgumentParser(
            prog="flare",
            description="FLARE CLI",
        )
        _GROUP_SUBPARSERS = _PARSER.add_subparsers(
            dest="group",
            required=True,
            title="command groups",
        )

    return _PARSER


def register_group(name, help):
    get_parser()
    parser = _GROUP_SUBPARSERS.add_parser(name, help=help)
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title=f"{name} commands",
    )
    return subparsers
