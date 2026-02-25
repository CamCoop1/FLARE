import pytest

from flare.cli.run.utils import load_settings_into_manager
from flare.src.fcc_analysis.dag_tooling.discovery import (
    discover_task_scripts,
    get_python_script_for_task,
)


@pytest.fixture(autouse=True, scope="function")
def setup_environment_for_discovery_testing(tmp_path):

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


def test_discover_task_scripts_for_valid_environment():
    """
    Test when we have a valid environment we pass the discover_task_scripts
    and returns the correct tasks
    """
    task_scripts = discover_task_scripts()
    assert len(task_scripts) == 2
    assert "stage2" in task_scripts
    assert "stage1" in task_scripts


def test_discover_task_scripts_for_invalid_environment(tmp_path):
    """
    Check the discover_task_scripts fails with an AssertionError
    when there are more than one script found for the same Task
    """
    stage1_again = tmp_path / "stage1_again.py"
    stage1_again.touch()

    with pytest.raises(AssertionError):
        _ = discover_task_scripts()


def test_get_python_script_for_task(tmp_path):
    """
    Test get_python_script_for_task works as intended and can get the task script
    """
    stage1_script = get_python_script_for_task("stage1")
    assert stage1_script.name == "stage1.py"
    assert stage1_script.parent == tmp_path

    stage2_script = get_python_script_for_task("stage2")
    assert stage2_script.name == "stage2.py"
    assert stage2_script.parent == tmp_path


def test_get_python_script_for_task_with_invalid_task_name():
    """
    Test that when a tasks python script cannot be found we raise an AssertionError
    """
    with pytest.raises(AssertionError):
        _ = get_python_script_for_task("stagefoo")
