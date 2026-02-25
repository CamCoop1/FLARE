import pytest

from flare.cli.run.utils import load_settings_into_manager
from flare.src.fcc_analysis.dag_tooling.builder import build_task_graph
from flare.src.pydantic_models.user_config_model import AddFlareTask
from flare.src.pydantic_models.utils import FlareTask


@pytest.fixture(autouse=True, scope="function")
def setup_environment_for_discovery_testing(tmp_path):
    """
    Base environment that will always be setup with a stage1 and stage2 script for every function called
    """

    class Args:
        study_dir = str(tmp_path)
        config_yaml = str(tmp_path)

        def pop(self, value, default):
            return default

    config_yaml = tmp_path / "config.yaml"
    config_yaml.touch()

    load_settings_into_manager(Args())

    stage1 = tmp_path / "stage1.py"
    stage1.touch()

    stage2 = tmp_path / "stage2.py"
    stage2.touch()

    yield

    config_yaml.unlink()
    stage1.unlink()
    stage2.unlink()


@pytest.fixture
def generic_flare_task():
    """
    Generic FlareTask with dummy inputs
    """
    return FlareTask(cmd="foo", args=[], output_file="bar")


@pytest.fixture
def internal_tasks(generic_flare_task):
    """
    Internal FCC Analysis Tasks for stage1 and stage2
    """
    tasks = dict()
    tasks["stage1"] = generic_flare_task
    tasks["stage2"] = generic_flare_task
    return tasks


@pytest.fixture
def user_tasks(generic_flare_task, tmp_path):
    """
    User added Tasks called stage0 and mystage which has their own requires and required_by
    """
    stage0 = tmp_path / "stage0.py"
    stage0.touch()

    mystage = tmp_path / "mystage.py"
    mystage.touch()

    tasks = dict()

    stage0_task = generic_flare_task.model_dump()
    stage0_task["required_by"] = ["stage1"]
    tasks["stage0"] = AddFlareTask(**stage0_task)

    mystage_task = generic_flare_task.model_dump()
    mystage_task["requires"] = "stage2"
    tasks["mystage"] = AddFlareTask(**mystage_task)
    return tasks


def test_build_task_graph_no_user_tasks(internal_tasks):
    """
    Call build_task_graph without any user_tasks and ensure the order is correct i.e

    stage1 -> stage2
    """
    dag = build_task_graph(internal_tasks=internal_tasks, user_tasks={})
    assert "stage1" in dag.flattened_dag_ordering
    assert "stage2" in dag.flattened_dag_ordering
    assert dag.dag["stage2"] == {"stage1"}


def test_build_task_graph_with_user_tasks(internal_tasks, user_tasks):
    """
    Call the build_task_graph function with both internal_tasks nad user_tasks
    and check that the Dag has been built properly i.e

    stage0 -> stage1 -> stage2 -> mystage
    """
    dag = build_task_graph(internal_tasks=internal_tasks, user_tasks=user_tasks)

    assert "stage1" in dag.flattened_dag_ordering
    assert "stage2" in dag.flattened_dag_ordering
    assert dag.dag["stage2"] == {"stage1"}

    assert "stage0" in dag.flattened_dag_ordering
    assert "mystage" in dag.flattened_dag_ordering
    assert dag.dag["stage1"] == {"stage0"}
    assert dag.dag["mystage"] == {"stage2"}


def test_build_task_graph_with_user_tasks_called_TaskRegistry(
    internal_tasks, user_tasks, mocker
):
    """
    Check that the TaskRegistry was called once when the build_task_graph function is called
    """
    mocked_TaskRegistry = mocker.patch(
        "flare.src.fcc_analysis.dag_tooling.builder.TaskRegistry"
    )
    _ = build_task_graph(internal_tasks=internal_tasks, user_tasks=user_tasks)
    mocked_TaskRegistry.assert_called_once()
