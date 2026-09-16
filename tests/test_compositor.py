from pathlib import Path

from PIL import Image, ImageDraw
import pytest

from mission_of_words.compositor import AssetPlacement, compose_search_find


def _icon(path: Path, color=(0, 0, 0, 255)) -> None:
    icon = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    draw.ellipse((10, 10, 90, 90), outline=color, width=5)
    icon.save(path)


def test_compositor_places_assets_and_returns_manifest(tmp_path: Path):
    background = tmp_path / "background.png"
    asset = tmp_path / "asset.png"
    output = tmp_path / "output.jpg"

    Image.new("RGB", (1000, 1200), "white").save(background)
    _icon(asset)

    manifest = compose_search_find(
        background,
        [AssetPlacement("test", asset, x_ratio=0.5, y_ratio=0.5, width_ratio=0.1)],
        output,
    )

    assert output.exists()
    assert len(manifest) == 1
    assert manifest[0]["name"] == "test"
    assert manifest[0]["width"] == 100
    assert manifest[0]["height"] == 100


def test_invalid_ratio_is_rejected(tmp_path: Path):
    background = tmp_path / "background.png"
    asset = tmp_path / "asset.png"
    output = tmp_path / "output.jpg"
    Image.new("RGB", (100, 100), "white").save(background)
    Image.new("RGBA", (10, 10), "black").save(asset)

    placement = AssetPlacement("bad", asset, x_ratio=1.2, y_ratio=0.5, width_ratio=0.1)
    try:
        compose_search_find(background, [placement], output)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid placement to raise ValueError")


def test_overlapping_targets_are_rejected(tmp_path: Path):
    background = tmp_path / "background.png"
    first = tmp_path / "a.png"
    second = tmp_path / "b.png"
    output = tmp_path / "output.jpg"
    Image.new("RGB", (400, 400), "white").save(background)
    _icon(first)
    _icon(second)
    with pytest.raises(ValueError, match="overlaps"):
        compose_search_find(
            background,
            [
                AssetPlacement("lantern", first, x_ratio=0.4, y_ratio=0.4, width_ratio=0.25),
                AssetPlacement("pumpkin", second, x_ratio=0.42, y_ratio=0.42, width_ratio=0.25),
            ],
            output,
        )
