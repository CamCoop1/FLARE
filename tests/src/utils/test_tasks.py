from itertools import pairwise

import b2luigi as luigi
import pytest

from flare.src.utils.tasks import OutputMixin, _linear_task_workflow_generator


@pytest.fixture(name="task_setup")
def linear_task_workflow_generator_setup():
    stages = ["stage1", "stage2", "stage3"]
    class_name = "MockClass"

    class MockLuigiClass(luigi.Task):
        pass

    return stages, class_name, MockLuigiClass


@pytest.fixture
def stage1_dependency_task():
    class MockStage1Dependency(luigi.Task):
        pass

    return MockStage1Dependency


def test__linear_task_workflow_generator_assertion_for_incorrect_base_class(task_setup):
    """Test that assertion error raised when base_class is not a subclass of luigi.Task"""
    stages, class_name, _ = task_setup
    base_class = type("IncorrectBaseClass", (), {})

    with pytest.raises(AssertionError):
        _linear_task_workflow_generator(
            stages=stages, class_name=class_name, base_class=base_class
        )


def test__linear_task_workflow_generator_assertion_for_incorrect_stages(task_setup):
    """Test that assertion error raised when stages is a list"""
    _, class_name, base_class = task_setup

    with pytest.raises(AssertionError):
        _linear_task_workflow_generator(
            stages="hello world", class_name=class_name, base_class=base_class
        )


def test__linear_task_workflow_generator_returned_task_inheritance(task_setup, mocker):
    """Test that the returned tasks inherit from OutputMixin and the given base_class"""
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")
    task_dict = _linear_task_workflow_generator(
        stages=stages, class_name=class_name, base_class=base_class
    )

    for task in task_dict.values():
        assert issubclass(task, OutputMixin)
        assert issubclass(task, base_class)

    assert mock_get_setting.call_count == len(stages)


def test__linear_task_workflow_generator_returned_task_standard_attributes(
    task_setup, mocker
):
    """Test that the returned tasks have attributes `stage` and `results_subdir`
    and that `stage` matches that given in the stages list and `results_subdir` matches that defined in src/__init__.py
    """
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")

    task_dict = _linear_task_workflow_generator(
        stages=stages, class_name=class_name, base_class=base_class
    )

    for stage, task in zip(stages, task_dict.values()):
        assert hasattr(task, "stage")
        assert getattr(task, "stage") == stage
        assert hasattr(task, "results_subdir")
        assert getattr(task, "results_subdir") == "/tmp/mock"

    assert mock_get_setting.call_count == len(stages)


def test__linear_task_workflow_generator_returned_task_additional_attributes_through_class_attrs(
    task_setup, mocker
):
    """Test that the returned tasks have the additional attributes passed to `class_attrs`"""

    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")
    task_dict = _linear_task_workflow_generator(
        stages=stages,
        class_name=class_name,
        base_class=base_class,
        class_attrs={s: {"hello": "world"} for s in stages},
    )

    for task in task_dict.values():
        assert hasattr(task, "hello")
        assert getattr(task, "hello") == "world"

    assert mock_get_setting.call_count == len(stages)


def test__linear_task_workflow_generator_tasks_dependency_set_correctly(
    task_setup, mocker
):
    """Test that the returned tasks have the correct dependency workflow defined
    by their `requires` function. E.g the Stage2 task should require the Stage1 task"""

    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")
    task_dict = _linear_task_workflow_generator(
        stages=stages,
        class_name=class_name,
        base_class=base_class,
    )

    for downstream_task, upstream_task in pairwise(reversed(task_dict.values())):
        required_task = next(downstream_task().requires())
        assert required_task == upstream_task()

    assert mock_get_setting.call_count == len(stages)


def test__linear_task_workflow_generator_inject_stage1_dependency_raises_AssertionError(
    task_setup, mocker
):
    """Test that when the injected stage1 dependency is not of type luigi.Task, AssertionError is raised
    using issubclass"""
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")

    class Stage1Dependency:
        pass

    with pytest.raises(AssertionError):
        _ = _linear_task_workflow_generator(
            stages=stages,
            class_name=class_name,
            base_class=base_class,
            inject_stage1_dependency=Stage1Dependency,
        )
    assert (
        mock_get_setting.call_count == 1
    )  # Upon creating the first task, the dependency injection raises AssertionError


def test__linear_task_workflow_generator_inject_stage1_dependency_success(
    task_setup, stage1_dependency_task, mocker
):
    """Test that the returned tasks have the correct dependency workflow defined
    by their `requires` function. E.g the Stage2 task should require the Stage1 task"""
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")
    task_dict = _linear_task_workflow_generator(
        stages=stages,
        class_name=class_name,
        base_class=base_class,
        inject_stage1_dependency=stage1_dependency_task,
    )
    # Get the stage1 task
    stage1_task = next(iter(task_dict.values()))()
    # Get the required task for Stage1
    required_task = next(stage1_task.requires())
    # Assert it is the task we injected
    assert required_task == stage1_dependency_task()
    assert mock_get_setting.call_count == len(stages)


def test__linear_task_workflow_generator_one_stage_only(task_setup, mocker):
    """Test that when given only a single task to create that it returns that task with no requires dependency"""
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")
    task_dict = _linear_task_workflow_generator(
        stages=[stages[0]],
        class_name=class_name,
        base_class=base_class,
    )

    assert len(task_dict.values()) == 1

    stage1_dict = next(iter(task_dict.values()))()

    assert stage1_dict.requires() == []
    assert mock_get_setting.call_count == 1


def test__linear_task_workflow_generator_one_stage_only_with_injected_dependency(
    task_setup, stage1_dependency_task, mocker
):
    """Test that when given only a single task to create that it returns that task with required stage1 dependency"""
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")
    task_dict = _linear_task_workflow_generator(
        stages=[stages[0]],
        class_name=class_name,
        base_class=base_class,
        inject_stage1_dependency=stage1_dependency_task,
    )

    assert len(task_dict.values()) == 1

    stage1_task = next(iter(task_dict.values()))()

    # Note the next() function will fail is requires() does not return a generator
    assert next(stage1_task.requires()) == stage1_dependency_task()
    assert mock_get_setting.call_count == 1


def test__linear_task_workflow_generator_injected_dependency_with_attributes(
    task_setup, stage1_dependency_task, mocker
):
    """Test that when a stage1 dependency and class attributes to attached to the injection, that
    the returned injected class has the class attributes"""
    stages, class_name, base_class = task_setup
    mock_get_setting = mocker.patch("b2luigi.get_setting", return_value="/tmp/mock")

    task_dict = _linear_task_workflow_generator(
        stages=[stages[0]],
        class_name=class_name,
        base_class=base_class,
        inject_stage1_dependency=stage1_dependency_task,
        class_attrs={"inject_stage1_dependency": {"prodtype": "mock"}},
    )

    assert len(task_dict.values()) == 1

    injected_task = next(next(iter(task_dict.values()))().requires())

    assert hasattr(injected_task, "prodtype")
    assert injected_task.prodtype == "mock"
    assert mock_get_setting.call_count == 1
