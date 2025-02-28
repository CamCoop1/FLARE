import pytest 

from src.mc_production.generator_specific_methods import MadgraphMethods
import src.mc_production.production_types as pt

def test_check_MadgraphMethods_class_has_correct_methods():
    """ 
    Ensure the Madgraph functions are correctly implemented 
    """
    assert hasattr(MadgraphMethods, 'madgraph_move_contents_to_tmp_output' )
    assert hasattr(MadgraphMethods, 'madgraph_copy_lhe_file_to_cwd' )
    


def test_BracketMappings_class_for_correct_attributes(get_valid_BracketMappings_mappings):
    for name, mapping in get_valid_BracketMappings_mappings:
        assert hasattr(pt.BracketMappings, name)
        assert getattr(pt.BracketMappings,name) == mapping

  
@pytest.mark.parametrize(
    "mapping, arg", 
    (
        ['()', '().root'],
        ['++', '++.py'],
        ['--', '--.lhe'],
        ['<>', 'card_<>.sin']
    )
)
def test_BracketMappings_for_valid_mapping(mapping, arg):
    assert pt.BracketMappings.determine_bracket_mapping(arg) == mapping
    
@pytest.mark.parametrize(
    "mapping, arg", 
    (
        ['()', '().root'],
        ['++', '++.py'],
        ['--', '--.lhe'],
        ['<>', 'card_<>.sin']
    )
)
def test_check_if_path_matches_mapping(mapping, arg):
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