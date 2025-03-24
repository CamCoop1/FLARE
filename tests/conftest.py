from functools import partial

import pytest


@pytest.fixture
def mc_production_types():
    return ["whizard", "madgraph"]


@pytest.fixture
def get_mapping_arg_pairs():
    return (["()", "().root"], ["++", "++.py"], ["--", "--.lhe"], ["<>", "card_<>.sin"])


@pytest.fixture
def get_valid_BracketMappings_mappings():
    return (
        ["output", "()"],
        ["input", "--"],
        ["datatype_parameter", "++"],
        ["free_name", "<>"],
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


@pytest.fixture
def get_whizard_mc_stage_config(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    mc_prod_dir = analysis_dir / "mc_production"
    mc_prod_dir.mkdir()

    details_yaml = mc_prod_dir / "details.yaml"

    details_yaml.write_text(
        """
        prodtype: whizard

        datatype:
          - wzp6_ee_mumuH_Hbb_ecm320
          - wzp6_ee_mumuH_Hbb_ecm240
          - wzp6_ee_mumuH_HWW_ecm365
        """
    )

    return mc_prod_dir


@pytest.fixture
def get_madgraph_mc_stage_config(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    mc_prod_dir = analysis_dir / "mc_production"
    mc_prod_dir.mkdir()

    details_yaml = mc_prod_dir / "details.yaml"

    details_yaml.write_text(
        """
        prodtype: madgraph

        datatype:
          - wzp6_ee_mumuH_Hbb_ecm320
          - wzp6_ee_mumuH_Hbb_ecm240
          - wzp6_ee_mumuH_HWW_ecm365
        """
    )

    return mc_prod_dir


@pytest.fixture
def get_full_madgraph_setup(tmp_path):
    datatype = "wzp6_ee_mumuH_Hbb_ecm320"

    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    mc_prod_dir = analysis_dir / "mc_production"
    mc_prod_dir.mkdir()

    details_yaml = mc_prod_dir / "details.yaml"

    details_yaml.write_text(
        f"""
        prodtype: madgraph

        datatype:
            - {datatype}
        """
    )

    runcard_dat = mc_prod_dir / f"{datatype}_runcard.dat"
    runcard_dat.write_text("")

    IDEA_card = mc_prod_dir / "card_lmao.tcl"
    IDEA_card.write_text("")

    edm4hep_card = mc_prod_dir / "edm4hep_lmao.tcl"
    edm4hep_card.write_text("")

    pythia_card = mc_prod_dir / "pythia_card_lmao.cmd"
    pythia_card.write_text("")

    stage1_prod_cmd = f"mg5_aMC {str(runcard_dat)}"
    stage2_prod_cmd = partial(
        "DelphesPythia8_EDM4HEP {0} {1} {2} {3}".format,
        str(IDEA_card),
        str(edm4hep_card),
        str(pythia_card),
    )

    return mc_prod_dir, datatype, stage1_prod_cmd, stage2_prod_cmd


@pytest.fixture
def get_full_whizard_setup(tmp_path):
    datatype = "wzp6_ee_mumuH_Hbb_ecm320"

    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    mc_prod_dir = analysis_dir / "mc_production"
    mc_prod_dir.mkdir()

    details_yaml = mc_prod_dir / "details.yaml"

    details_yaml.write_text(
        f"""
        prodtype: whizard

        datatype:
            - {datatype}
        """
    )

    sin_file = mc_prod_dir / f"{datatype}.sin"
    sin_file.write_text("")

    IDEA_card = mc_prod_dir / "card_lmao.tcl"
    IDEA_card.write_text("")

    edm4hep_card = mc_prod_dir / "edm4hep_lmao.tcl"
    edm4hep_card.write_text("")

    stdhep_file = mc_prod_dir / "proc.stdhep"
    stdhep_file.write_text("")

    stage1_prod_cmd = f"whizard {str(sin_file)}"
    stage2_prod_cmd = partial(
        "DelphesSTDHEP_EDM4HEP {0} {1} {3} {2}".format,
        str(IDEA_card),
        str(edm4hep_card),
    )

    return mc_prod_dir, datatype, stage1_prod_cmd, stage2_prod_cmd
