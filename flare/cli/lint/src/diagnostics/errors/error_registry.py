from enum import Enum

from flare.cli.lint.src.diagnostics.errors.definitions import (
    Error,
    ErrorExceptions,
    ErrorLevel,
)
from flare.cli.lint.src.pydantic_models import AnalyzerModel


class FlareErrors(Enum):
    """This enum works as a registry for all Flare Errors"""

    def checker_func(self, analyzer: AnalyzerModel):
        """Little cheat to not have to call .value all the time"""
        return self.value.checker_func(analyzer)

    @property
    def specific_error_exceptions(self):
        return self.value.exceptions

    FLARE001 = Error(
        description="No inputDir defined in analysis script",
        level=ErrorLevel.INFO,
        suggestion="Ensure you have defined an inputDir for this class",
        checker_func=lambda model: "inputDir" not in model.flaggable_variables.keys(),
        exceptions=[ErrorExceptions.INPUTDIR_NOT_REQUIRED],
    )
    FLARE002 = Error(
        description="No outputDir defined in analysis script",
        level=ErrorLevel.INFO,
        checker_func=lambda model: "outputDir" not in model.flaggable_variables.keys(),
        suggestion="Ensure you have defined an outputDir for this class",
    )
    FLARE003 = Error(
        description="Path does not derive from inputDir or outputDir",
        level=ErrorLevel.ERROR,
        checker_func=lambda model: {
            m.name: m
            for m in model.identified_path_variables.values()
            # Check if the path does not reference inputDir or outputDir
            if not any(
                j == k for k in model.flaggable_variables.keys() for j in m.references
            )
            # Check the user has not set noqa
            and not m.noqa
            # Check the name of the variable is not known to flaggable_variables
            and not any(m.name == k for k in model.flaggable_variables.keys())
        },
        suggestion="Ensure you have defined your paths with an f-string using bases of inputDir or outputDir",
    )
    FLARE004 = Error(
        description="Noqa found during search",
        level=ErrorLevel.INFO,
        checker_func=lambda model: {
            m.name: m for m in model.identified_path_variables.values() if m.noqa
        },
        suggestion="Path skipped due to #noqa instance",
    )
