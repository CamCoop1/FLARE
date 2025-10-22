import pytest

import flare.src.utils.logo as logo_module


@pytest.fixture
def print_flare_logo():
    # No longer print the animation
    #    loading_animation()
    return r"""



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

"""


def test_logo_module_has_print_flare_logo():
    assert hasattr(logo_module, "print_flare_logo")


def test_print_flare_logo_prints_correct_logo(capsys, print_flare_logo):
    logo_module.print_flare_logo()
    captured = capsys.readouterr()
    assert print_flare_logo.strip() in captured.out.strip()
