from src.utils.dirs import find_file
from src.utils.yaml import get_config


def test_definitions_file_in_src_directory():
    """
    Check that the definitons.py module exists in the src directory
    """
    path = find_file("src", "definitions.py")
    assert path.exists()


def test_BASE_DIRECTORY_in_definitons():
    """
    Ensure the BASE_DIRECTORY exists
    """
    import src.definitions as defs

    assert hasattr(defs, "BASE_DIRECTORY")


def test_production_types_yaml_in_mc_production():
    """
    Ensure the production_types.yaml exists
    """
    prod_types_file = find_file("src", "mc_production", "production_types.yaml")
    assert prod_types_file.exists()


def test_production_types_yaml_not_empty(mc_production_types):
    """
    Test taht the production_types.yaml is not empty
    """
    prod_types_dir = find_file("src", "mc_production")

    content = get_config("production_types.yaml", dir=prod_types_dir)

    assert all([prod_type in content.keys() for prod_type in mc_production_types])
