import pytest

from flare.cli.lint.src.diagnostics.errors.definitions import (
    ErrorExceptions,
    ErrorLevel,
)
from flare.cli.lint.src.diagnostics.flare_fcc_diagnostics import (
    generate_flare_diagnostics,
)
from flare.cli.lint.src.pydantic_models import AnalyzerModel


@pytest.fixture
def analyzer_model() -> AnalyzerModel:
    """Generic AnalyzerModel to be used in testing"""
    analyzer_model = (
        AnalyzerModel.register_flaggable_variable(
            "inputDir", value="hello/world", lineno=24
        )
        .register_identified_path_variables(
            name="inputdir",
            path="hello/world",
            is_fstring=False,
            references=[],
            noqa=True,
            lineno=30,
            end_lineno=30,
        )
        .register_identified_path_variables(
            name="this_path",
            path="f'{inputdir}/hello/world'",
            is_fstring=True,
            references=["inputdir"],
            noqa=False,
            lineno=124,
            end_lineno=215,
        )
    )
    return analyzer_model.validate_registered_data()


@pytest.mark.parametrize(
    "error_level, expected_errors",
    [e for e in zip(ErrorLevel, [1, 2, 3, 3])],
)
def test_generate_flare_diagnostics_for_ErrorLevels_no_exceptions(
    analyzer_model, error_level, expected_errors
):
    """Test the generate flare diagnostics works for all Error Levels"""
    diags = generate_flare_diagnostics(
        analyzer_model, filename="foo", error_level=error_level
    )
    assert len([d for d in diags if not d.suppressed]) == expected_errors


@pytest.mark.parametrize(
    "error_level, expected_errors",
    [e for e in zip(ErrorLevel, [1, 2, 3, 3])],
)
def test_generate_flare_diagnostics_for_ErrorLevels_with_INPUTDIR_NOT_REQUIRED_exception(
    analyzer_model, error_level, expected_errors
):
    """Test the generate flare diagnostics works for all Error Levels with
    exception INPUTDIR_NOT_REQUIRED"""
    diags = generate_flare_diagnostics(
        analyzer_model,
        filename="foo",
        error_level=error_level,
        exceptions=[ErrorExceptions.INPUTDIR_NOT_REQUIRED],
    )
    assert len([d for d in diags if not d.suppressed]) == expected_errors
