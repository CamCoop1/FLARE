import sys
import time

import b2luigi as luigi

from src.fcc_analysis.tasks import FCCAnalysisWrapper
from src.utils.stages import check_for_unregistered_stage_file


def loading_animation():
    print("Warming up b2luigi... ", end="")
    for _ in range(3):
        for char in "|/-\\":
            sys.stdout.write(f"\033[1;32m{char}\033[0m")  # Green spinner
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")
    print("\033[1;32mDone!\033[0m 🎉")


def print_b2luigi_logo():
    loading_animation()
    logo = r"""
# ---------------------------------------------------------------------------------------------------------------------------
#    FFFFFFFF    CCCCCC     CCCCCC       ++       BBBBB       22 2   LLL       UUU    UUU   IIIIIIII    GGGGGG    IIIIIIII
#    FF         CC         CC            ++       B    BB    2  2    LLL       UUU    UUU      II      GG            II
#    FFFFFF     CC         CC       +++++++++++   BBBBB        2     LLL       UUU    UUU      II      GG   GGGG     II
#    FF         CC         CC            ++       B    BB     2      LLL       UUU    UUU      II      GG     GG     II
#    FF          CCCCCC     CCCCCC       ++       BBBBB      222222  LLLLLLLL   UUUUUUUU    IIIIIIII    GGGGGG    IIIIIIII
# ---------------------------------------------------------------------------------------------------------------------------
"""
    print(logo)
    print("Hello .. Launching into Luigi-powered awesomeness! 🌟💻")


if __name__ == "__main__":

    print_b2luigi_logo()
    if check_for_unregistered_stage_file():
        raise RuntimeError(
            "There exists unregistered stages in your analysis. Please register them following the README.md"
            " and rerun"
        )

    luigi.process(FCCAnalysisWrapper(), workers=4, batch=True)
