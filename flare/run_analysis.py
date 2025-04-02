import b2luigi as luigi

from flare.src.fcc_analysis.fcc_stages import Stages
from flare.src.fcc_analysis.tasks import FCCAnalysisWrapper
from flare.src.utils.logo import print_b2luigi_logo


def main(executable=list[str]):
    print_b2luigi_logo()
    if Stages.check_for_unregistered_stage_file():
        raise RuntimeError(
            "There exists unregistered stages in your analysis. Please register them following the README.md"
            " and rerun"
        )

    luigi.set_setting("filename", "")
    luigi.set_setting("executable", executable)

    luigi.process(
        FCCAnalysisWrapper(),
        workers=4,
        batch=True,
        ignore_additional_command_line_args=True,
    )


if __name__ == "__main__":
    main()
