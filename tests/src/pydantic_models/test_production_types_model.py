import pytest
from pydantic import ValidationError

from flare.src.pydantic_models.production_types_model import (
    FCCProductionModel,
    MCProductionModel,
)


@pytest.fixture
def default_stage_args():
    return {"cmd": "mock_cmd", "args": ["mock_arg"], "output_file": "mock_output_file"}


def test_valid_fcc_production_model(default_stage_args):
    """Given valid FCCProductionModel input, check output is as expected"""
    model = FCCProductionModel(**{"fccanalysis": {"stage1": default_stage_args}}).dict()

    assert model["fccanalysis"]["stage1"]["cmd"] == default_stage_args["cmd"]
    assert model["fccanalysis"]["stage1"]["args"] == default_stage_args["args"]
    assert (
        model["fccanalysis"]["stage1"]["output_file"]
        == default_stage_args["output_file"]
    )


def test_valid_mc_production_model(default_stage_args):
    """
    Given valid production types and stages, check output is correct
    """
    model = MCProductionModel(
        **{
            "whizard": {"stage1": default_stage_args},
            "madgraph": {"stage1": default_stage_args},
            "pythia8": {"stage1": default_stage_args},
        }
    ).dict()

    assert model["whizard"]["stage1"]["cmd"] == default_stage_args["cmd"]
    assert model["madgraph"]["stage1"]["args"] == default_stage_args["args"]
    assert (
        model["pythia8"]["stage1"]["output_file"] == default_stage_args["output_file"]
    )


def test_fcc_model_missing_required_field():
    """
    Test ValidationError for invalid key for FCCProductionModel
    """
    with pytest.raises(ValidationError):
        FCCProductionModel(
            **{"invalid": {"config": {"param": 42}}}  # missing 'executable'
        )


def test_mc_model_with_extra_field(default_stage_args):
    """
    Test when given an extra field, the MCProductionModel returns a ValidationError
    """
    with pytest.raises(ValidationError) as excinfo:
        MCProductionModel(
            **{
                "whizard": {"stage1": default_stage_args},
                "madgraph": {"stage1": default_stage_args},
                "pythia8": {"stage1": default_stage_args},
                "invalid": {},
            }
        ).dict()

    assert "Extra inputs are not permitted" in str(excinfo.value)


def test_production_type_with_extra_inner_field(default_stage_args):
    """
    Test ValidationError when extra fields are added to the internal Stage
    """
    default_stage_args["invalid"] = "invalid"

    with pytest.raises(ValidationError) as excinfo:
        FCCProductionModel(**{"fccanalysis": {"stage1": default_stage_args}})
    assert "Extra inputs are not permitted" in str(excinfo.value)
