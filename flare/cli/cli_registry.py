import argparse
from dataclasses import dataclass
from typing import Callable, Optional

_PARSER = None
_GROUP_SUBPARSERS = None
_GROUP_HOOKS = {}


@dataclass
class GroupHooks:
    pre_parse: Optional[Callable] = None
    post_parse: Optional[Callable] = None


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


def register_group(name, help, hooks: GroupHooks | None = None):
    get_parser()

    parser = _GROUP_SUBPARSERS.add_parser(name, help=help)
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title=f"{name} commands",
    )

    if hooks:
        _GROUP_HOOKS[name] = hooks

    return subparsers
