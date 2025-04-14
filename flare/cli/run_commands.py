import b2luigi as luigi

import flare
from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.fcc_analysis.tasks import FCCAnalysisWrapper
from flare.src.mc_production.tasks import MCProductionWrapper


def run_mcproduction(args):
    """Run the MC Production workflow"""
    config = luigi.get_setting("dataprod_config")

    flare.process(
        MCProductionWrapper(prodtype=config["global_prodtype"]),
        workers=20,
        batch=True,
        ignore_additional_command_line_args=True,
        flare_args=args,
        from_cli_input=True,
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
        workers=20,
        batch=True,
        ignore_additional_command_line_args=True,
        flare_args=args,
        from_cli_input=True,
    )
