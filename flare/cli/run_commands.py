import b2luigi as luigi

import flare
from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.fcc_analysis.tasks import FCCAnalysisWrapper
from flare.src.mc_production.mc_production_types import get_mc_production_types
from flare.src.mc_production.tasks import MCProductionWrapper


def _check_mc_prod_valid(prodtype: str):
    """Check that the production type given in the mc_production yaml
    if valid"""
    try:
        _ = get_mc_production_types()[prodtype]
    except KeyError:
        raise KeyError(
            f'MC production type {prodtype} is not valid. Valid prod types are {" ".join(get_mc_production_types().values())}'
        )


def run_mcproduction(args):
    """Run the MC Production workflow"""
    config = luigi.get_setting("dataprod_config")
    _check_mc_prod_valid(config["prodtype"])
    flare.process(
        MCProductionWrapper(prodtype=config["prodtype"]),
        workers=4,
        batch=True,
        ignore_additional_command_line_args=True,
        flare_args=args,
    )


def run_analysis(args):
    """Run the Analysis workflow"""
    if Stages.check_for_unregistered_stage_file():
        raise RuntimeError(
            "There exists unregistered stages in your analysis. Please register them following the README.md"
            " and rerun"
        )

    assert (
        Stages.get_stage_ordering()
    ), "Not FCC Stages have been detected in your study directory"
    flare.process(
        FCCAnalysisWrapper(),
        workers=4,
        batch=True,
        ignore_additional_command_line_args=True,
        flare_args=args,
    )
