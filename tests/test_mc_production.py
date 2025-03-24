import importlib

import pytest

import src.mc_production.production_types as pt
import src.mc_production.tasks as tasks
from src.mc_production.generator_specific_methods import MadgraphMethods
from src.mc_production.production_types import get_mc_production_types


def test_check_MadgraphMethods_class_has_correct_methods():
    """
    Ensure the Madgraph functions are correctly implemented
    """
    assert hasattr(MadgraphMethods, "madgraph_move_contents_to_tmp_output")
    assert hasattr(MadgraphMethods, "madgraph_copy_lhe_file_to_cwd")


def test_BracketMappings_class_for_correct_attributes(
    get_valid_BracketMappings_mappings,
):
    """
    Test that that BracketMappings have the correct attributes
    """
    for name, mapping in get_valid_BracketMappings_mappings:
        assert hasattr(pt.BracketMappings, name)
        assert getattr(pt.BracketMappings, name) == mapping


def test_BracketMappings_for_valid_mapping(get_mapping_arg_pairs):
    """
    Test BracketMappings.determine_bracket_mapping function to ensure it correctly
    identifies the mapping from a given argument
    """
    for mapping, arg in get_mapping_arg_pairs:
        assert pt.BracketMappings.determine_bracket_mapping(arg) == mapping


def test_check_if_path_matches_mapping(get_mapping_arg_pairs):
    """
    Tests the check_if_path_matches_mapping function in which an argument a path and a mapping are
    provided and it returns true if that mapping is apart of that path
    """
    for mapping, arg in get_mapping_arg_pairs:
        assert pt.check_if_path_matches_mapping(arg, arg, mapping)


@pytest.mark.parametrize(
    "mapping, arg, path",
    (["()", "++.root", "path/to/().root"], ["()", "--.root", "path/to/++.root"]),
)
def test_check_if_path_matches_mapping_fails(mapping, arg, path):
    """
    Check path_matches_mapping function working correctly
    """
    assert not pt.check_if_path_matches_mapping(arg, path, mapping)


@pytest.mark.parametrize(
    "prod_type, n_stages",
    [("get_whizard_mc_stage_config", 2), ("get_madgraph_mc_stage_config", 2)],
)
def test_create_mc_stage_classes(request, prod_type, n_stages):
    """
    Check that when whizard and madgraph setup, there are two MC production stage tasks
    """
    tasks.prod_config_dir = request.getfixturevalue(prod_type)
    output_tasks = tasks._create_mc_stage_classes()
    assert len(output_tasks) == n_stages


def test_get_last_stage_task_on_whizard(get_whizard_mc_stage_config):
    """
    Check the get_last_stage_task returns the correct final task
    """
    tasks.prod_config_dir = get_whizard_mc_stage_config
    last_stage = tasks.get_last_stage_task()
    assert "stage2" in last_stage.__name__


def test_get_mc_production_type_fails_with_unknown_generator():
    """
    Test that KeyError is raised when unknown production type is selected
    """
    # Because _create_mc_stage_classes is a cached function, trying to change the
    # _prod_config function without reloading the module will cause unexpected behaviour
    importlib.reload(tasks)
    tasks._prod_config = lambda: {"prodtype": "fakegenerator"}
    with pytest.raises(KeyError):
        tasks._create_mc_stage_classes()


def test_collect_cmd_inputs_for_magraph(get_full_madgraph_setup):
    """
    Here we  will test the collect_cmd_inputs function works as intended
    """
    # First we unpack the fixture
    mc_prod_dir, datatype, stage1_prod_cmd, stage2_prod_cmd = get_full_madgraph_setup
    # must reload the tasks module as to have a clean slate
    importlib.reload(tasks)
    # Set the mc_prod_dir inside the taks module
    tasks.prod_config_dir = mc_prod_dir
    # Get the stage tasks for madgraph production
    run_tasks = tasks._create_mc_stage_classes()
    # Zip the stage tasks and their expected outputs
    for raw_task, prod_cmd in zip(
        run_tasks.values(), [stage1_prod_cmd, stage2_prod_cmd]
    ):
        # Initilaise the task with the prodtype and datatype
        task = raw_task(
            prodtype=get_mc_production_types()["madgraph"], datatype=datatype
        )
        if task.stage == "stage2":
            # if its stage2 we must add the output file to the command as this is done during runtime
            prod_cmd = prod_cmd(str(task.tmp_output_parent_dir / task.output_file_name))
        # Assert these commands are equal
        assert task.prod_cmd == prod_cmd


def test_collect_cmd_inputs_for_whizard(get_full_whizard_setup):
    """
    Here we  will test the collect_cmd_inputs function works as intended
    """
    # First we unpack the fixture
    mc_prod_dir, datatype, stage1_prod_cmd, stage2_prod_cmd = get_full_whizard_setup
    # must reload the tasks module as to have a clean slate
    importlib.reload(tasks)
    # Set the mc_prod_dir inside the taks module
    tasks.prod_config_dir = mc_prod_dir
    # Get the stage tasks for madgraph production
    run_tasks = tasks._create_mc_stage_classes()
    # Zip the stage tasks and their expected outputs
    for raw_task, prod_cmd in zip(
        run_tasks.values(), [stage1_prod_cmd, stage2_prod_cmd]
    ):
        # Initilaise the task with the prodtype and datatype
        task = raw_task(
            prodtype=get_mc_production_types()["whizard"], datatype=datatype
        )
        if task.stage == "stage2":
            # if its stage2 we must add the output file to the command as this is done during runtime aswell as the input file
            prod_cmd = prod_cmd(
                str(task.input_file_path),
                str(task.tmp_output_parent_dir / task.output_file_name),
            )

        # Assert these commands are equal
        assert task.prod_cmd == prod_cmd


def test_requires_func_correctly_identifies_required_tasks(get_whizard_mc_stage_config):
    """
    Check that the requires function of MCProductionBaseTask is correctly identifying dependencies
    """
    tasks.prod_config_dir = get_whizard_mc_stage_config
    output_tasks = tasks._create_mc_stage_classes()

    for raw_task, value in zip(output_tasks.values(), [False, True]):
        task = raw_task(prodtype=get_mc_production_types()["whizard"], datatype="")
        # list will have one element if required task. Will be [] if no task is required
        assert bool([r for r in task.requires()]) == value
