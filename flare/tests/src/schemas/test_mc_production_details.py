import json

import jsonschema
import pytest

from flare.src import find_file

SCHEMA_PATH = find_file("flare/src/schemas/mc_production_details.json")


@pytest.fixture
def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def test_mc_production_details_schema_exists():
    assert SCHEMA_PATH.exists()


@pytest.mark.parametrize(
    "data, is_valid",
    [
        # Valid case with required fields
        ({"prodtype": "madgraph", "datatype": ["data1", "data2"]}, True),
        # Invalid case: Missing required field "prodtype"
        ({"datatype": ["data1", "data2"]}, False),
        # Invalid case: prodtype not in enum
        ({"prodtype": "invalidtype", "datatype": ["data1", "data2"]}, False),
        # Invalid case: datatype not an array
        ({"prodtype": "madgraph", "datatype": "not_an_array"}, False),
        # Invalid case: Extra field not allowed
        (
            {
                "prodtype": "whizard",
                "datatype": ["data1", "data2"],
                "extra_field": "not allowed",
            },
            False,
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
