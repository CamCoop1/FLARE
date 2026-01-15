"""
These tests pertain to the AnalyzerModel Pydantic Model that has been attapted to work
as a registry.

The idea being we can register all our data using the builder method into a database. Then when we
are ready, we can validate the data using the Pydantic infrastructure.

We need not test the Pydantic API as we are trusting that the Pydantic package is properly tested and works
as intended. These tests are only for the additional features we add to our models.
"""

import pytest

from flare.cli.lint.src.pydantic_models import AnalyzerModel


@pytest.fixture
def known_VALID_VARIABLE_KEYS():
    """Here we define the known VALID_VARIABLE_KEYS known to be in use.
    This should be updated when/if new ones are added
    """
    return {"inputDir", "outputDir"}


@pytest.fixture
def valid_identified_path_variable_object():
    return {
        "name": "variable_name",
        "path": "/hello/world",
        "is_fstring": False,
        "references": [],
        "noqa": False,
        "lineno": 12,
        "end_lineno": 12,
    }


def test_AnalyzerModel_has_intializer():
    """Test to check the AnalyzerModel has the class method initialize_register_mode"""
    assert hasattr(AnalyzerModel, "initialize_register_mode")


def test_AnalyzerModel_has_flaggable_variable_registry():
    """Test to check the AnalyzerModel has the class method register_flaggable_variable"""
    assert hasattr(AnalyzerModel, "register_flaggable_variable")


def test_AnalyzerModel_has_identified_path_variables_registry():
    """Test to check the AnalyzerModel has the class method register_identified_path_variables"""
    assert hasattr(AnalyzerModel, "register_identified_path_variables")


def test_AnalyzerModel_has_registered_identified_path_variables():
    """Test to check the AnalyzerModel has the class method registered_identified_path_variables"""
    assert hasattr(AnalyzerModel, "registered_identified_path_variables")


def test_AnalyzerModel_has_validate_registered_data():
    """Test to check the AnalyzerModel has the class method validate_registered_data"""
    assert hasattr(AnalyzerModel, "validate_registered_data")


def test_AnalyzerModel_has_VALID_VARIABLE_KEYS(known_VALID_VARIABLE_KEYS):
    """Test to check the AnalyzerModel has the attribute VALID_VARIABLE_KEYS"""
    assert hasattr(AnalyzerModel, "VALID_VARIABLE_KEYS")
    assert AnalyzerModel.VALID_VARIABLE_KEYS == known_VALID_VARIABLE_KEYS


def test_AnalyzerModel_for_valid_register_flaggable_variable():
    """Test that the register_flaggable_variable function works as intended"""
    analyzer = AnalyzerModel.initialize_register_mode()
    analyzer.register_flaggable_variable("inputDir", value="/hello/world", lineno=25)


def test_AnalyzerModel_for_invalid_register_flaggable_variable_key_on_validation():
    """Test that the register_flaggable_variable function raises ValueError"""
    analyzer = AnalyzerModel.initialize_register_mode()
    analyzer.register_flaggable_variable(
        "invalid_name", value="/hello/world", lineno=25
    )
    with pytest.raises(ValueError):
        analyzer.validate_registered_data()


def test_AnalyzerModel_for_valid_register_identified_path_variables_on_validation(
    valid_identified_path_variable_object,
):
    """Test that the register_identified_path_variables works as intended"""
    analyzer = AnalyzerModel.initialize_register_mode()
    analyzer.register_identified_path_variables(**valid_identified_path_variable_object)
    analyzer.validate_registered_data()


def test_AnalyzerModel_for_registered_identified_path_variables_call(
    valid_identified_path_variable_object,
):
    """Test that the registered_identified_path_variables works as intended"""
    analyzer = AnalyzerModel.initialize_register_mode()
    analyzer.register_identified_path_variables(**valid_identified_path_variable_object)
    # Remove the 'name' variable as this is used as a key in the database dictionary
    name = valid_identified_path_variable_object["name"]
    # We dict() call the returned value from our database as it is a Pydantic Model
    assert (
        analyzer.registered_identified_path_variables()[name].dict()
        == valid_identified_path_variable_object
    )
