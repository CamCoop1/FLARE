# RANGES, 6..8, 11
from typing import Protocol


class Foo(Protocol):
    """
    Here is the doc string, located on line 7
    """

    def bar(self):
        """Here is a function doc string on line"""
        ...
