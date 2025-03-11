import pytest 


from src.mc_production.generator_specific_methods import MadgraphMethods
import src.mc_production.production_types as pt
import src.mc_production.tasks as tasks


def test_check_MadgraphMethods_class_has_correct_methods():
    """ 
    Ensure the Madgraph functions are correctly implemented 
    """
    assert hasattr(MadgraphMethods, 'madgraph_move_contents_to_tmp_output' )
    assert hasattr(MadgraphMethods, 'madgraph_copy_lhe_file_to_cwd' )
    


def test_BracketMappings_class_for_correct_attributes(get_valid_BracketMappings_mappings):
    """ 
    Test that that BracketMappings have the correct attributes 
    """
    for name, mapping in get_valid_BracketMappings_mappings:
        assert hasattr(pt.BracketMappings, name)
        assert getattr(pt.BracketMappings,name) == mapping

  
def test_BracketMappings_for_valid_mapping(get_mapping_arg_pairs):
    """ 
    Test BracketMappings.determine_bracket_mapping function to ensure it correctly
    identifies the mapping from a given argument
    """
    for (mapping, arg) in get_mapping_arg_pairs:
        assert pt.BracketMappings.determine_bracket_mapping(arg) == mapping
    

def test_check_if_path_matches_mapping(get_mapping_arg_pairs):
    """ 
    Tests the check_if_path_matches_mapping function in which an argument a path and a mapping are
    provided and it returns true if that mapping is apart of that path
    """
    for (mapping, arg) in get_mapping_arg_pairs:
        assert pt.check_if_path_matches_mapping(arg, arg, mapping)
    
@pytest.mark.parametrize(
    "mapping, arg, path", 
    (
        ['()', '++.root', "path/to/().root"],
        ['()', '--.root', "path/to/++.root"]
 
    )
)
def test_check_if_path_matches_mapping(mapping, arg, path):
    assert not pt.check_if_path_matches_mapping(arg, path, mapping)
    
def test_create_mc_stage_classes(get_whizard_mc_stage_config):
    
    tasks.prod_config_dir = get_whizard_mc_stage_config 
    output_tasks = tasks._create_mc_stage_classes()
    assert len(output_tasks) == 2
    
def test_create_mc_stage_classes(get_madgraph_mc_stage_config):
    
    tasks.prod_config_dir = get_madgraph_mc_stage_config 
    output_tasks = tasks._create_mc_stage_classes()
    assert len(output_tasks) == 2
    
def test_get_last_stage_task_on_whizard(get_whizard_mc_stage_config):
    
    tasks.prod_config_dir = get_whizard_mc_stage_config 
    last_stage = tasks.get_last_stage_task()
    assert 'stage2' in last_stage.__name__
    
    