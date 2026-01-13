from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

from flare.cli.lint.src.pydantic_models import AnalyzerModel


class ErrorLevel(Enum):
    """Flare error levels"""

    INFO = auto()
    ERROR = auto()
    PANIC = auto()


class ErrorExceptions(Enum):
    """Flare error exceptions. The idea is that is an error is found but it is
    expected or not needed we can tell Flare to ignore it"""

    INPUTDIR_NOT_REQUIRED = auto()


@dataclass
class Error:
    """This dataclass holds the information for a Flare Error"""

    description: str
    level: ErrorLevel
    suggestion: str
    checker_func: Callable[[AnalyzerModel], bool | dict]
    exceptions: list[ErrorExceptions] = field(default_factory=list)
