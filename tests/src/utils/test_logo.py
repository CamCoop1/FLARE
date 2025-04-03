import pytest

import flare.src.utils.logo as logo


@pytest.fixture
def fcc_b2luigi_logo():
    return r"""
 ---------------------------------------------------------------------------------------------------------------------------
    FFFFFFFF    CCCCCC     CCCCCC       ++       BBBBB       22 2   LLL       UUU    UUU   IIIIIIII    GGGGGG    IIIIIIII
    FF         CC         CC            ++       B    BB    2  2    LLL       UUU    UUU      II      GG            II
    FFFFFF     CC         CC       +++++++++++   BBBBB        2     LLL       UUU    UUU      II      GG   GGGG     II
    FF         CC         CC            ++       B    BB     2      LLL       UUU    UUU      II      GG     GG     II
    FF          CCCCCC     CCCCCC       ++       BBBBB      222222  LLLLLLLL   UUUUUUUU    IIIIIIII    GGGGGG    IIIIIIII
 ---------------------------------------------------------------------------------------------------------------------------
"""


def test_logo_module_has_loading_animation():
    assert hasattr(logo, "loading_animation")


def test_logo_module_has_print_b2luigi_logo():
    assert hasattr(logo, "print_b2luigi_logo")


def test_print_b2luigi_logo_prints_correct_logo(capsys, fcc_b2luigi_logo):
    logo.print_b2luigi_logo()
    captured = capsys.readouterr()
    assert fcc_b2luigi_logo.strip() in captured.out.strip()
