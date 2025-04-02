import json

import jsonschema
import pytest

from flare.src import find_file

SCHEMA_PATH = find_file("flare/src/schemas/production_types.json")


@pytest.fixture
def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def test_production_types_schema_exists():
    assert SCHEMA_PATH.exists()


@pytest.mark.parametrize(
    "data, is_valid",
    [
        # Valid case with required fields
        (
            {
                "fccanalysis": {
                    "stage1": {
                        "cmd": "run_analysis",
                        "args": ["--input", "file1.root"],
                        "output_file": "output1.root",
                    }
                }
            },
            True,
        ),
        # Invalid case: Missing required field "cmd"
        (
            {
                "fccanalysis": {
                    "stage1": {
                        "args": ["--input", "file1.root"],
                        "output_file": "output1.root",
                    }
                }
            },
            False,
        ),
        # Invalid case: Additional property not allowed
        (
            {
                "fccanalysis": {
                    "stage1": {
                        "cmd": "run_analysis",
                        "args": ["--input", "file1.root"],
                        "output_file": "output1.root",
                        "extra_field": "not allowed",
                    }
                }
            },
            False,
        ),
        # Invalid case: args not an array
        (
            {
                "fccanalysis": {
                    "stage1": {
                        "cmd": "run_analysis",
                        "args": "not_an_array",
                        "output_file": "output1.root",
                    }
                }
            },
            False,
        ),
        # Valid case with optional fields "pre_run" and "on_completion"
        (
            {
                "fccanalysis": {
                    "stage1": {
                        "cmd": "run_analysis",
                        "args": ["--input", "file1.root"],
                        "output_file": "output1.root",
                        "pre_run": ["setup.sh"],
                        "on_completion": ["cleanup.sh"],
                    }
                }
            },
            True,
        ),
    ],
)
def test_json_schema(load_schema, data, is_valid):
    schema = load_schema
    if is_valid:
        jsonschema.validate(instance=data, schema=schema)
    else:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)
