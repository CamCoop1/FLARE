import pytest

from flare.src.fcc_analysis.dag_tooling.validation import validate_no_overlap


def test_validate_no_overlap_with_no_overlap():
    """
    Test that when two sets have no overlap, nothing occurs
    """
    set1 = {"1", "2", "3"}
    set2 = {"4", "5", "6"}

    validate_no_overlap(set1, set2)


def test_validate_no_overlap_with_with_overlap():
    """
    Test when two sets DO overlap, a ValueError is raised
    """
    set1 = {"4", "2", "3"}
    set2 = {"4", "5", "6"}

    with pytest.raises(ValueError):
        validate_no_overlap(set1, set2)
