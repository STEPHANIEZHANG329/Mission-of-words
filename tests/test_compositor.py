from pathlib import Path

from PIL import Image, ImageDraw

from mission_of_words.compositor import AssetPlacement, compose_search_find


def test_compositor_places_assets_and_returns_manifest(tmp_path: Path):
    background = tmp_path / "background.png"
    asset = tmp_path / "asset.png"
    output = tmp_path / "output.jpg"

    Image.new("RGB", (1000, 1200), "white").save(background)
    icon = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    draw.ellipse((10, 10, 90, 90), outline="black", width=5)
    icon.save(asset)

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
