import pytest
from pydantic_core import ValidationError

from flare.src.pydantic_models.user_config_model import AddFlareTask, UserConfigModel


@pytest.fixture
def basic_flare_task_dict():
    return {"cmd": "foo", "args": [], "output_file": "bar"}


@pytest.fixture
def basic_add_stage_dict(basic_flare_task_dict):
    add_stage = dict()
    add_stage["stage1"] = AddFlareTask(requires="stage0", **basic_flare_task_dict)
    add_stage["stage2"] = AddFlareTask(requires="stage1", **basic_flare_task_dict)
    add_stage["stage0"] = AddFlareTask(required_by=["stage1"], **basic_flare_task_dict)

    return add_stage


def test_AddFlareTask_for_check_at_least_one_validation_VALID_INPUTS(
    basic_flare_task_dict,
):
    """
    Test for valid AddFlareTask data no ValueErrors are raised
    """
    _ = AddFlareTask(requires="StageFoo", **basic_flare_task_dict)

    _ = AddFlareTask(required_by=["StageBar"], **basic_flare_task_dict)


def test_AddFlareTask_for_check_at_least_one_validation_INVALID_INPUTS(
    basic_flare_task_dict,
):
    """
    Check that if an AddFlareTask has no requires or required_by we raise an ValueError
    """
    with pytest.raises(ValueError):
        _ = AddFlareTask(**basic_flare_task_dict)


def test_UserConfigModel_check_no_two_stages_have_same_required_by_assertion_error(
    basic_add_stage_dict,
):
    """
    Test that our validation that no two tasks have the same 'required_by' works
    correctly
    """
    basic_add_stage_dict["stageneg1"] = basic_add_stage_dict["stage0"]

    with pytest.raises(ValidationError):
        _ = UserConfigModel(add_stage=basic_add_stage_dict)


def test_UserConfigModel_captures_extra_fields_under_model_extra():
    """
    Test that extra fields fed to the UserConfigModel are captures inside the
    model_extra field
    """
    model = UserConfigModel(batch_system="slurm")
    batch_system = model.model_extra.get("batch_system")
    assert batch_system is not None
    assert batch_system == "slurm"
