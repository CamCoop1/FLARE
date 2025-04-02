import json

import jsonschema
import pytest

from flare.src import find_file

SCHEMA_PATH = find_file("flare/src/schemas/config_details.json")


@pytest.fixture
def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def test_config_details_schema_exists():
    assert SCHEMA_PATH.exists()


@pytest.mark.parametrize(
    "data, is_valid",
    [
        # Valid case with all required fields
        (
            {
                "Name": "TestConfig",
                "Version": "1.0",
                "Description": "This is a test configuration.",
            },
            True,
        ),
        # Missing required field "Name"
        ({"Version": "1.0", "Description": "This is a test configuration."}, False),
        # Extra field not allowed (additionalProperties=false)
        (
            {
                "Name": "TestConfig",
                "Version": "1.0",
                "Description": "This is a test configuration.",
                "ExtraField": "Not allowed",
            },
            False,
        ),
        # StudyDir should default to "analysis" but is optional
        (
            {
                "Name": "TestConfig",
                "Version": "1.0",
                "Description": "This is a test configuration.",
                "StudyDir": "custom_dir",
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
