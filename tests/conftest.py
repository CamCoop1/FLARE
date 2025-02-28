import pytest
import os

@pytest.fixture
def get_valid_BracketMappings_mappings():
    return (
        ['output', '()'], 
        ['input', '--'],
        ['datatype_parameter', '++'],
        ['free_name', '<>']        
    )     

@pytest.fixture
def setup_correct_analysis_dir(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    # Create some example files
    file1 = analysis_dir / "stage1.py"
    file2 = analysis_dir / "stage2.py"
    file3 = analysis_dir / "plot.py"
    
    file1.write_text("inputdir = /here/.")
    file2.write_text("This is file 2")
    file3.write_text("This is file 3")
    
    
    return analysis_dir


@pytest.fixture
def setup_analysis_for_unregistered_stage_file(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    # Create some example files
    file1 = analysis_dir / "stage1.py"
    file2 = analysis_dir / "dummy.py"
    
    
    file1.write_text("This is file 1")
    file2.write_text("This is file 2")
    
    return analysis_dir

@pytest.fixture
def setup_analysis_files_for_Errors(tmp_path):
    """ 
    Setup the analysis/  directory with two 'stage1' files
    """
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    # Create some example files
    file1 = analysis_dir / "stage1.py"
    file2 = analysis_dir / "stage1_dummy.py"

    file1.write_text("This is file 1")
    file2.write_text("This is file 2")


    return analysis_dir
