import pytest

from flare.src import find_file
from flare.src.utils.jinja2_utils import get_template


def test_template_module_contains_steering_file_template():
    """Test that the template module has `steering_file.jinja2"""
    assert find_file("src", "templates", "steering_file.jinja2").exists()


@pytest.mark.parametrize(
    "context, expected_strings",
    [
        # Case 1: All fields are provided
        (
            {
                "outputdir_string": "OUTDIR",
                "outputDir": "/path/to/output",
                "inputDir": "/path/to/input",
                "python_code": "print('Hello')",
            },
            [
                'OUTDIR = "/path/to/output"',
                'inputDir = "/path/to/input"',
                "print('Hello')",
            ],
        ),
        # Case 2: inputDir is missing
        (
            {
                "outputdir_string": "OUTDIR",
                "outputDir": "/path/to/output",
                "inputDir": None,
                "python_code": "print('Hello')",
            },
            [
                'OUTDIR = "/path/to/output"',
                "print('Hello')",
            ],  # inputDir should not appear
        ),
    ],
)
def test_template_for_outputDir(context, expected_strings):
    """Test that the template has the fields outputdir_string, outputDir, inputDir and python_code exist and work"""
    template = get_template("steering_file.jinja2")
    rendered_output = template.render(context)

    for expected in expected_strings:
        assert (
            expected in rendered_output
        ), f"Expected '{expected}' in rendered template, but got:\n{rendered_output}"
