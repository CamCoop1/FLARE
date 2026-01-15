import shutil
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


def print_flare_logo():
    # No longer print the animation
    #    loading_animation()
    logo = r"""



 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |  _________   | || |   _____      | || |      __      | || |  _______     | || |  _________   | |
| | |_   ___  |  | || |  |_   _|     | || |     /  \     | || | |_   __ \    | || | |_   ___  |  | |
| |   | |_  \_|  | || |    | |       | || |    / /\ \    | || |   | |__) |   | || |   | |_  \_|  | |
| |   |  _|      | || |    | |   _   | || |   / ____ \   | || |   |  __ /    | || |   |  _|  _   | |
| |  _| |_       | || |   _| |__/ |  | || | _/ /    \ \_ | || |  _| |  \ \_  | || |  _| |___/ |  | |
| | |_____|      | || |  |________|  | || ||____|  |____|| || | |____| |___| | || | |_________|  | |
| |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'

                            Github: [ https://github.com/CamCoop1/FLARE ]
                            arXiv : [ https://arxiv.org/abs/2506.16094 ]

""".strip(
        "\n"
    )
    lines = logo.splitlines()
    term_width = shutil.get_terminal_size(fallback=(80, 20)).columns
    art_width = max(len(line) for line in lines)

    pad = max(0, (term_width - art_width) // 2)

    for line in lines:
        print(" " * pad + line)
    print("Hello .. Launching into b2Luigi-powered awesomeness! 🌟💻")


if __name__ == "__main__":
    print_flare_logo()
