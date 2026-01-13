from flare.cli.lint.src.diagnostics.errors.definitions import ErrorExceptions
from flare.cli.lint.src.diagnostics.errors.error_registry import FlareErrors
from flare.cli.lint.src.pydantic_models import AnalyzerModel, Diagnostic


def emit_error_to_diagnostic(
    code: str,
    level: str,
    message: str,
    filename: str,
    *,
    lineno=1,
    end_lineno=1,
    context=None,
):
    return Diagnostic(
        code=code,
        level=level,
        message=message,
        file=filename,
        lineno=lineno,
        end_lineno=end_lineno,
        context=context or {},
    )


def generate_flare_diagnostics(
    analysis: AnalyzerModel, filename: str, exceptions: list[ErrorExceptions] = []
):
    diags = []

    for error in FlareErrors:
        if any(e in error.specific_error_exceptions for e in exceptions):
            continue
        result = error.checker_func(analysis)
        error_value = error.value
        # If the result is a Falsey type, we continue to the next error
        if not result:
            continue

        match result:
            case bool():
                diags.append(
                    emit_error_to_diagnostic(
                        code=error.name,
                        level=error_value.level.name,
                        message=error_value.description,
                        filename=filename,
                    )
                )
            case dict():
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
                        )
                    )

    return diags
