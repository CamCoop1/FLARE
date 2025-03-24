import src.utils.tasks as tasks
from src.utils.dirs import find_file


def test_OutputMixin_class_log_dir_and_result_dir():
    """
    Test the OutputMixin class log_dir and results_dir operates as expected when

    - not being inherited
    - is inherited
    - is inherited with results_subdir
    """
    # Test when using OutputMixin as the main class
    OutputMixin_name = tasks.OutputMixin.__name__
    expected_log_dir = find_file("log", OutputMixin_name)
    expected_results_dir = find_file("data", OutputMixin_name)

    assert tasks.OutputMixin().log_dir == expected_log_dir
    assert tasks.OutputMixin().result_dir == expected_results_dir

    # Create an class that inherits from OutputMixin
    class foo(tasks.OutputMixin):
        pass

    expected_log_dir = find_file("log", foo.__name__)
    expected_results_dir = find_file("data", foo.__name__)

    assert foo().log_dir == expected_log_dir
    assert foo().result_dir == expected_results_dir

    # Make a class that inherits from OutputMixin and sets the results_subdir
    class bar(tasks.OutputMixin):
        results_subdir = "par"

    expected_log_dir = find_file("log", bar.results_subdir, bar.__name__)
    expected_results_dir = find_file("data", bar.results_subdir, bar.__name__)

    assert bar().log_dir == expected_log_dir
    assert bar().result_dir == expected_results_dir
