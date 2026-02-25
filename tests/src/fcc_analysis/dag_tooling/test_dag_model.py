import pytest
from pydantic import ValidationError

from flare.src.fcc_analysis.dag_tooling.dag_model import Dag


@pytest.fixture
def valid_dag_dict():
    return {"2": {"1"}, "3": {"2"}}


def test_Dag_for_valid_dag_dict(valid_dag_dict):
    """
    Test when a valid dag dict is passed to the Dag object,
    it validates correctly
    """
    assert Dag(valid_dag_dict)


def test_Dag_for_invalid_dag_dict(valid_dag_dict):
    downstream, upstream = next(iter(valid_dag_dict.items()))

    valid_dag_dict[list(upstream)[0]] = {downstream}
    invalid_dag_dict = valid_dag_dict

    with pytest.raises(ValidationError):
        Dag(invalid_dag_dict)


def test_Dag_for_dag_property(valid_dag_dict):
    """
    Ensure the Dag object has a dag property
    """
    dag = Dag(valid_dag_dict)
    assert hasattr(dag, "dag")


def test_dag_for_correct_roots_of_dag(valid_dag_dict):
    """
    Check that the Dag object is correctly able to determine
    the roots of our DAG, i.e the very last tasks that would be ran in our workflow
    """
    dag = Dag(valid_dag_dict)
    roots = dag.get_roots_of_dag()
    # Check the returned value is a set
    assert isinstance(roots, set)
    # Check the returned set is just "3"
    assert roots == {"3"}

    # Add another root to the dag
    valid_dag_dict["4"] = {"2"}
    dag = Dag(valid_dag_dict)
    roots = dag.get_roots_of_dag()
    # Check the returned set now contains both "3" and "4"
    assert roots == {"3", "4"}
