import pytest
from pydantic import ValidationError

from flare.src.pydantic_models.user_mcprod_config_model import UserMCProdConfigModel


def test_extra_arguments_not_allowd():
    """
    Test that given extra arguments the pydantic model raises an
    """
    with pytest.raises(ValidationError) as f:
        _ = UserMCProdConfigModel(extra_variable=[])

    assert "extra fields not permitted" in str(f.value)


def test_valid_global_prodtype_with_strings():
    """
    Test when global_prodtype is set and datatype is correctly configured,
    the pydantic model is successful
    """
    config = UserMCProdConfigModel(
        global_prodtype="madgraph", datatype=["data1", "data2"]
    )
    assert config.global_prodtype == "madgraph"
    assert config.datatype == ["data1", "data2"]


def test_valid_default_prodtype_with_dicts():
    """
    Test when no global_prodtype is set and correct datatype
    is configured, the pydantic model is successful
    """
    config = UserMCProdConfigModel(
        datatype=[
            {"data1": {"prodtype": "madgraph"}},
            {"data2": {"prodtype": "whizard"}},
        ]
    )
    assert config.datatype[0]["data1"]["prodtype"] == "madgraph"


def test_invalid_global_prodtype_with_non_list():
    """
    Test ValidationError when global_prodtype is set and datatype is not a list
    """
    with pytest.raises(ValidationError) as excinfo:
        UserMCProdConfigModel(global_prodtype="whizard", datatype="not-a-list")
    assert "datatype must be a list" in str(excinfo.value)


def test_invalid_global_prodtype_with_dicts():
    """
    Test ValidationError when global_prodtype is set and datatype is set for
    local_prodtype per dataset fails
    """
    with pytest.raises(ValidationError) as excinfo:
        UserMCProdConfigModel(
            global_prodtype="whizard", datatype=[{"data1": {"prodtype": "madgraph"}}]
        )
    assert "each type in the datatype list must be a string" in str(excinfo.value)


def test_invalid_default_prodtype_with_string():
    """
    Test ValidationError when global_prodtype is not set and the datatype is configured
    to be a list but not of dictionaries
    """
    with pytest.raises(ValidationError) as excinfo:
        UserMCProdConfigModel(datatype=["not-a-dict"])
    assert "each datatype must be a dictionary" in str(excinfo.value)


def test_invalid_missing_prodtype():
    """
    Test ValidationError when no global_prodtype is parsed but the datatype dictionaries do not
    contain a prodtype key value pair
    """
    with pytest.raises(ValidationError) as excinfo:
        UserMCProdConfigModel(datatype=[{"data1": {}}])
    assert "There is no prodtype in the datatype dictionary" in str(excinfo.value)


def test_invalid_inner_prodtype_value():
    """
    Test ValidationError when global_prodtype is not set but the local prodtype dictionary
    does not contain a valid prodtype
    """
    with pytest.raises(ValidationError) as excinfo:
        UserMCProdConfigModel(datatype=[{"data1": {"prodtype": "invalid_type"}}])
    assert "Invalid prodtype" in str(excinfo.value)
