from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

from flare.cli.lint.src.pydantic_models import AnalyzerModel


class ErrorLevel(Enum):
    """Flare error levels"""

    INFO = auto()
    ERROR = auto()
    PEDANTIC = auto()
    PANIC = auto()


class ErrorExceptions(Enum):
    """Flare error exceptions. The idea is that is an error is found but it is
    expected or not needed we can tell Flare to ignore it"""

    INPUTDIR_NOT_REQUIRED = auto()
    OUTPUTDIR_NOT_REQUIRED = auto()


@dataclass
class Error:
    """This dataclass holds the information for a Flare Error"""

    # Description of what the error is
    description: str
    # The severity level of the error
    level: ErrorLevel
    # Suggestions for why the error occurred
    suggestion: str

    # The function which checks if an error should be called
    # Takes the AnalyzerModel and returns a bool or a dict object
    # to be handled by the diagnostic tool
    checker_func: Callable[[AnalyzerModel], bool | dict]
    # If an exception is passed to the diagnostic tools then
    # we skip errors which include these exceptions
    exceptions: list[ErrorExceptions] = field(default_factory=list)
