from enum import Enum

from flare.cli.lint.src.diagnostics.errors.definitions import (
    Error,
    ErrorExceptions,
    ErrorLevel,
)
from flare.cli.lint.src.pydantic_models import AnalyzerModel


class FlareErrors(Enum):
    """This enum works as a registry for all Flare Errors"""

    def __str__(self) -> str:
        indent_size = " " * 6
        output_string_list = [self.name]
        output_string_list += [f"{indent_size}Description → {self.value.description}"]
        output_string_list += [f"{indent_size}Error Level → {self.value.level.name}"]

        return "\n".join(output_string_list)

    def checker_func(self, analyzer: AnalyzerModel):
        """Little cheat to not have to call .value all the time"""
        return self.value.checker_func(analyzer)

    @property
    def specific_error_exceptions(self):
        """Returns the error exceptions of a specific error when called"""
        return self.value.exceptions

    FLARE001 = Error(
        description="No inputDir defined in analysis script",
        level=ErrorLevel.INFO,
        suggestion=(
            "The first stage of your FCCAnalysis workflow needs a defined inputDir when not"
            " running the MCProduction workflow. Ensure you have defined an inputDir for this script"
        ),
        checker_func=lambda model: "inputDir" not in model.flaggable_variables.keys(),
        # Note we are excluding this error when the diagnostic tool is passed ErrorExceptions.INPUTDIR_NOT_REQUIRED
        exceptions=[ErrorExceptions.INPUTDIR_NOT_REQUIRED],
    )
    FLARE002 = Error(
        description="No outputDir defined in analysis script",
        level=ErrorLevel.INFO,
        checker_func=lambda model: "outputDir" not in model.flaggable_variables.keys(),
        suggestion="Ensure you have defined an outputDir for this script",
        exceptions=[ErrorExceptions.OUTPUTDIR_NOT_REQUIRED],
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
        suggestion=(
            "Ensure you have defined your paths with an f-string using bases of inputDir or outputDir. FLARE requires full control of input "
            "and output directories, governed by the inputDir and outputDir variables which are overwritten at run time. If this is expected, add #noqa at the end of this variable declaration"
        ),
    )
    FLARE004 = Error(
        description="Noqa found during search",
        level=ErrorLevel.PEDANTIC,
        checker_func=lambda model: {
            m.name: m for m in model.identified_path_variables.values() if m.noqa
        },
        suggestion="Path skipped due to #noqa instance, logged for book keeping",
    )
    FLARE100 = Error(
        description="outputDir identified, will be overwritten",
        level=ErrorLevel.PEDANTIC,
        checker_func=lambda model: "outputDir" in model.flaggable_variables.keys(),
        suggestion="FLARE has identified that you have declared an outputDir. FLARE will overwrite this during runtime.",
    )
    FLARE101 = Error(
        description="inputDir identified, will be overwritten",
        level=ErrorLevel.PEDANTIC,
        checker_func=lambda model: "inputDir" in model.flaggable_variables.keys(),
        suggestion="FLARE has identified that you have declared an inputDir. FLARE will overwrite this during runtime.",
    )
    FLARE102 = Error(
        description="outdir identified in PLOT stage, will be overwritten",
        level=ErrorLevel.PEDANTIC,
        checker_func=lambda model: "outdir" in model.flaggable_variables.keys(),
        suggestion="FLARE has identified that you have declared an outputDir. FLARE will overwrite this during runtime.",
    )
    FLARE200 = Error(
        description="Python script is empty. Cannot proceed with an empty python script",
        level=ErrorLevel.ERROR,
        checker_func=lambda model: model.script_is_empty,
        suggestion="You must populate your python script with code",
    )
