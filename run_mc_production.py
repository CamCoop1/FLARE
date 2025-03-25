import sys
import time

import b2luigi as luigi

from src.mc_production.production_types import get_mc_production_types
from src.mc_production.tasks import MCProductionWrapper
from src.utils.yaml import get_config


def _check_mc_prod_valid(prodtype: str):
    try:
        _ = get_mc_production_types()[prodtype]
    except KeyError:
        raise KeyError(
            f'MC production type {prodtype} is not valid. Valid prod types are {" ".join(get_mc_production_types().values())}'
        )


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
    config = get_config("details.yaml", dir="analysis/mc_production")
    _check_mc_prod_valid(config["prodtype"])

    luigi.process(
        MCProductionWrapper(prodtype=config["prodtype"]), workers=4, batch=True
    )
