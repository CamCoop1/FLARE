from itertools import pairwise

import b2luigi as luigi
import pytest

from flare.src import find_file, results_subdir
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


def test_OutputMixin_no_results_subdir():
    """Check OutputMixin returns correct log_dir and result_dir
    when no results_subdir is passed to the class"""
    mock_instance = OutputMixin()

    assert mock_instance.log_dir == find_file("log", mock_instance.__class__.__name__)
    assert mock_instance.result_dir == find_file(
        "data", mock_instance.__class__.__name__
    )


def test_OutputMixin_results_subdir():
    """Check OutputMixin returns correct log_dir and result_dir
    when results_subdir is passed to the class"""
    mock_instance = OutputMixin()
    mock_instance.results_subdir = "test"

    assert mock_instance.log_dir == find_file(
        "log", "test", mock_instance.__class__.__name__
    )
    assert mock_instance.result_dir == find_file(
        "data", "test", mock_instance.__class__.__name__
    )


def test_OutputMixin_inheritance():
    """Check OutputMixin returns correct log_dir and result_dir
    when inherited by a child class"""

    class MockClass(OutputMixin):
        pass

    mock_instance = MockClass()
    assert mock_instance.log_dir == find_file("log", mock_instance.__class__.__name__)
    assert mock_instance.result_dir == find_file(
        "data", mock_instance.__class__.__name__
    )


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


def test__linear_task_workflow_generator_returned_task_inheritance(task_setup):
    """Test that the returned tasks inherit from OutputMixin and the given base_class"""
    stages, class_name, base_class = task_setup

    task_dict = _linear_task_workflow_generator(
        stages=stages, class_name=class_name, base_class=base_class
    )

    for task in task_dict.values():
        assert issubclass(task, OutputMixin)
        assert issubclass(task, base_class)


def test__linear_task_workflow_generator_returned_task_standard_attributes(task_setup):
    """Test that the returned tasks have attributes `stage` and `results_subdir`
    and that `stage` matches that given in the stages list and `results_subdir` matches that defined in src/__init__.py
    """
    stages, class_name, base_class = task_setup

    task_dict = _linear_task_workflow_generator(
        stages=stages, class_name=class_name, base_class=base_class
    )

    for stage, task in zip(stages, task_dict.values()):
        assert hasattr(task, "stage")
        assert getattr(task, "stage") == stage
        assert hasattr(task, "results_subdir")
        assert getattr(task, "results_subdir") == results_subdir


def test__linear_task_workflow_generator_returned_task_additional_attributes_through_class_attrs(
    task_setup,
):
    """Test that the returned tasks have the additional attributes passed to `class_attrs`"""

    stages, class_name, base_class = task_setup

    task_dict = _linear_task_workflow_generator(
        stages=stages,
        class_name=class_name,
        base_class=base_class,
        class_attrs={s: {"hello": "world"} for s in stages},
    )

    for task in task_dict.values():
        assert hasattr(task, "hello")
        assert getattr(task, "hello") == "world"


def test__linear_task_workflow_generator_tasks_dependency_set_correctly(task_setup):
    """Test that the returned tasks have the correct dependency workflow defined
    by their `requires` function. E.g the Stage2 task should require the Stage1 task"""

    stages, class_name, base_class = task_setup

    task_dict = _linear_task_workflow_generator(
        stages=stages,
        class_name=class_name,
        base_class=base_class,
    )

    for downstream_task, upstream_task in pairwise(reversed(task_dict.values())):
        required_task = next(downstream_task().requires())
        assert required_task == upstream_task()


def test__linear_task_workflow_generator_inject_stage1_dependency_raises_AssertionError(
    task_setup,
):
    """Test that when the injected stage1 dependency is not of type luigi.Task, AssertionError is raised
    using issubclass"""
    stages, class_name, base_class = task_setup

    class Stage1Dependency:
        pass

    with pytest.raises(AssertionError):
        _ = _linear_task_workflow_generator(
            stages=stages,
            class_name=class_name,
            base_class=base_class,
            inject_stage1_dependency=Stage1Dependency,
        )


def test__linear_task_workflow_generator_inject_stage1_dependency_success(
    task_setup, stage1_dependency_task
):
    """Test that the returned tasks have the correct dependency workflow defined
    by their `requires` function. E.g the Stage2 task should require the Stage1 task"""
    stages, class_name, base_class = task_setup

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


def test__linear_task_workflow_generator_one_stage_only(task_setup):
    """Test that when given only a single task to create that it returns that task with no requires dependency"""
    stages, class_name, base_class = task_setup

    task_dict = _linear_task_workflow_generator(
        stages=[stages[0]],
        class_name=class_name,
        base_class=base_class,
    )

    assert len(task_dict.values()) == 1

    stage1_dict = next(iter(task_dict.values()))()

    assert stage1_dict.requires() == []


def test__linear_task_workflow_generator_one_stage_only_with_injected_dependenct(
    task_setup, stage1_dependency_task
):
    """Test that when given only a single task to create that it returns that task with required stage1 dependency"""
    stages, class_name, base_class = task_setup

    task_dict = _linear_task_workflow_generator(
        stages=[stages[0]],
        class_name=class_name,
        base_class=base_class,
        inject_stage1_dependency=stage1_dependency_task,
    )

    assert len(task_dict.values()) == 1

    stage1_dict = next(iter(task_dict.values()))()

    # Note the next() function will fail is requires() does not return a generator
    assert next(stage1_dict.requires()) == stage1_dependency_task()
