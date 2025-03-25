import sys
import time


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
 ---------------------------------------------------------------------------------------------------------------------------
    FFFFFFFF    CCCCCC     CCCCCC       ++       BBBBB       22 2   LLL       UUU    UUU   IIIIIIII    GGGGGG    IIIIIIII
    FF         CC         CC            ++       B    BB    2  2    LLL       UUU    UUU      II      GG            II
    FFFFFF     CC         CC       +++++++++++   BBBBB        2     LLL       UUU    UUU      II      GG   GGGG     II
    FF         CC         CC            ++       B    BB     2      LLL       UUU    UUU      II      GG     GG     II
    FF          CCCCCC     CCCCCC       ++       BBBBB      222222  LLLLLLLL   UUUUUUUU    IIIIIIII    GGGGGG    IIIIIIII
 ---------------------------------------------------------------------------------------------------------------------------
"""
    print(logo)
    print("Hello .. Launching into b2Luigi-powered awesomeness! 🌟💻")
