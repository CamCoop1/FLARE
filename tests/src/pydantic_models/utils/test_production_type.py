import pytest

from flare.src.pydantic_models.utils.flare_task import FlareTask
from flare.src.pydantic_models.utils.production_type import ProductionTypeBaseModel


@pytest.fixture
def default_flare_task():
    return FlareTask(
        cmd="run.sh", args=["--input", "file.txt"], output_file="output.root"
    )


@pytest.fixture
def default_productiontypebasemodel(default_flare_task):
    prodtype_model = ProductionTypeBaseModel(
        {"stage1": default_flare_task, "stage2": default_flare_task}
    )
    return prodtype_model


def test_flaretask_model_works_as_dict(default_productiontypebasemodel):
    """
    Test the Mapping inheritance is working correctly and makes the
    ProductionTypeModel act like a dictionary
    """
    prodtype_model = default_productiontypebasemodel
    assert prodtype_model["stage1"]
    assert prodtype_model["stage2"]


def test_flaretask_model_works_for_length(default_productiontypebasemodel):
    """
    Test the Mapping inheritance is working and the len function is
    working correctly
    """
    prodtype_model = default_productiontypebasemodel

    assert len(prodtype_model) == 2
