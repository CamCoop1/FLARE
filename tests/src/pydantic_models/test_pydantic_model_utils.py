import pytest
from pydantic import ValidationError, RootModel

from flare.src.pydantic_models.utils import ProductionTypeBaseModel, StageModel


@pytest.fixture
def default_stage_data():
    return {
        "cmd": "run.sh",
        "args": ["--input", "file.txt"],
        "output_file": "output.root",
    }


@pytest.fixture
def default_prod_data():
    return {
        "madgraph": {
            "cmd": "run.sh",
            "args": ["--input", "file.txt"],
            "output_file": "output.root",
        },
        "whizard": {
            "cmd": "doit.sh",
            "args": ["--cfg", "config.json"],
            "output_file": "result.root",
        },
    }


def test_valid_stage(default_stage_data):
    """
    Test a valid stage data config
    """

    stage = StageModel(**default_stage_data)
    assert stage.cmd == "run.sh"
    assert stage.on_completion == []  # default
    assert stage.pre_run == []  # default


def test_stage_with_extras_should_fail(default_stage_data):
    """
    Test unexpected values are not allowed
    """
    default_stage_data.update({"unexpected": "not allowed"})

    with pytest.raises(ValidationError) as excinfo:
        StageModel(**default_stage_data)

    assert "Extra inputs are not permitted" in str(excinfo.value)


def test_stage_with_optional_fields(default_stage_data):
    """
    Test optional fields are added correctly
    """
    default_stage_data.update({"on_completion": ["stage2"], "pre_run": ["stage0"]})

    s = StageModel(**default_stage_data)
    assert s.on_completion == ["stage2"]
    assert s.pre_run == ["stage0"]


def test_production_type_model_valid(default_prod_data):
    """
    Test the model is correctly handling the RootModel
    functionality and will act as a dict
    """
    assert issubclass(ProductionTypeBaseModel, RootModel)
    model = ProductionTypeBaseModel.parse_obj(default_prod_data)
    assert hasattr(model, 'root')
    assert "madgraph" in model.keys()
    assert model["whizard"].cmd == "doit.sh"


def test_production_type_model_rejects_extra_in_stage(default_prod_data):
    """
    Test ProductionTypeModel rejects unexpected field
    """
    data = {}
    for key, value in default_prod_data.items():
        data[key] = value.update({"extra_field": "not allowed"})

    with pytest.raises(ValidationError):
        ProductionTypeBaseModel.parse_obj(data)
