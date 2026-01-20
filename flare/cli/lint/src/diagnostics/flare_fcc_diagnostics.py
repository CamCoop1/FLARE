import shutil

from colorama import Fore

from flare.cli.lint.src.diagnostics.errors.definitions import (
    ErrorExceptions,
    ErrorLevel,
)
from flare.cli.lint.src.diagnostics.errors.error_registry import FlareErrors
from flare.cli.lint.src.pydantic_models import AnalyzerModel, Autofix, Diagnostic


def emit_error_to_diagnostic(
    code: str,
    level: str,
    message: str,
    filename: str,
    suggestion: str,
    *,
    suppressed=False,
    lineno=1,
    end_lineno=1,
    context=None,
    replacement=None,
):
    """
    Function servers to separate the emittion of an error from just calling Diagnostic. In case the in the future
    additional things must be done when omitting the error, we can place them here.
    """
    return Diagnostic(
        code=code,
        level=level,
        message=message,
        file=filename,
        lineno=lineno,
        end_lineno=end_lineno,
        context=context or {},
        suppressed=suppressed,
        autofix=Autofix(description=suggestion, replacement=replacement),
    )


def generate_flare_diagnostics(
    analysis: AnalyzerModel,
    filename: str,
    exceptions: list[ErrorExceptions] = [],
    error_level: ErrorLevel = ErrorLevel.ERROR,
):
    """Generate FLARE diagnostics from the AnalyzerModel. We do this by looping through the FlareErrors
    and emitting errors only when we are returned a truthy value i.e a bool or a dict from the checker_func of
    our error"""
    diags = []

    for error in FlareErrors:
        if any(e in error.specific_error_exceptions for e in exceptions):
            continue
        result = error.checker_func(analysis)
        error_value = error.value
        # If the result is a Falsey type, we continue to the next error
        if not result:
            continue

        # Match on the type of result, if its a bool or dict changes how we want to handle it
        match result:
            case bool():
                diags.append(
                    emit_error_to_diagnostic(
                        code=error.name,
                        level=error_value.level.name,
                        message=error_value.description,
                        filename=filename,
                        # Because the ErrorLevel enum uses auto() it has automatic numbering.
                        # Say INFO = 0 and ERROR = 1, if we pass to this function
                        # error_level=ErrorLevel.INFO then we suppress all errors which are higher
                        suppressed=(error_level.value < error_value.level.value),
                        suggestion=error_value.suggestion,
                    )
                )
            case dict():
                # For each IdentifiedPathEntry(ForbidExtraBaseModel collected, raise an error
                for model in result.values():
                    diags.append(
                        emit_error_to_diagnostic(
                            code=error.name,
                            level=error_value.level.name,
                            message=error_value.description,
                            filename=filename,
                            lineno=model.lineno,
                            end_lineno=model.end_lineno,
                            context={model.name: model.path},
                            suppressed=(error_level.value < error_value.level.value),
                            suggestion=error_value.suggestion,
                        )
                    )

    return diags


def print_diagnostics(diagnostics: list[Diagnostic]):
    """Print our diagnostics for the user to read."""
    _diagnostics_banner()
    INDENT_VALUE = " " * 6
    for d in diagnostics:
        if d.suppressed:
            continue

        print(
            ">>",
            Fore.LIGHTRED_EX + f"[{d.code}:{d.level}]",
            Fore.WHITE + f"{d.file}:{d.lineno}-{d.end_lineno}",
        )
        print(INDENT_VALUE, f"→ {d.message}")
        if d.context:
            for variable, path in d.context.items():
                print(INDENT_VALUE, f"→ Variable: {variable}, Value: {path}")
        if d.autofix:
            print(INDENT_VALUE, f"→ Auto suggestion: {d.autofix.description}")
            if d.autofix.replacement:
                print(INDENT_VALUE, f"→ Replacement: {d.autofix.replacement}")
        print("")


def print_no_diagnostics_to_show():
    _diagnostics_banner(title="No Flare Linter Diagnostic Errors :)")


def _diagnostics_banner(title="Flare Linter Diagnostics"):
    width = shutil.get_terminal_size(fallback=(80, 20)).columns

    text = f" {title} "
    pad = max(0, width - len(text))
    left = pad // 2
    right = pad - left

    line = "=" * left + text + "=" * right
    print(line)
