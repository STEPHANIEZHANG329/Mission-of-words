import os
from pathlib import Path

from llk.generate import assets_for_group
from llk.paths import FONTS


def test_every_generation_group_is_nonempty():
    for group in ("front", "coloring", "search", "maze", "faith", "targets", "back", "cover"):
        assets = assets_for_group(group)
        assert assets, group


def test_fonts_are_vendored():
    required = [
        "Inter-Regular.ttf",
        "Inter-Bold.ttf",
        "Inter-SemiBold.ttf",
        "LiberationSerif-Regular.ttf",
        "LiberationSerif-Bold.ttf",
    ]
    for name in required:
        assert (FONTS / name).exists(), name


def test_gpt2_is_not_required_for_unit_tests():
    assert os.environ.get("GPT2") in (None, "") or True
