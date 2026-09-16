"""Compose-path compile check using local fixture images. Never shipped."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from llk.compose import Composer
from llk.cover import CoverComposer
from llk.paths import ASSETS_ACCEPTED
from llk.spec import load_spec


@pytest.fixture
def fixture_art(tmp_path, monkeypatch):
    spec = load_spec()
    folder = tmp_path / "accepted"
    folder.mkdir()
    for asset in spec.assets:
        img = Image.new("RGB", (128, 192 if asset.size.endswith("1536") else 128), (245, 245, 245))
        # Non-uniform so later QA wouldn't treat it as blank if reused by mistake.
        for i in range(8, 120, 16):
            img.putpixel((i, i % img.size[1]), (20, 20, 20))
        dest = folder / f"{asset.asset_id}.jpg"
        img.save(dest, "JPEG", quality=80)

    import llk.images as images

    def fake_find(asset_id: str) -> Path:
        path = folder / f"{asset_id}.jpg"
        if not path.exists():
            raise FileNotFoundError(asset_id)
        return path

    monkeypatch.setattr(images, "find_art", fake_find)
    monkeypatch.setattr("llk.compose.find_art", fake_find)
    return folder


def test_compose_interior_and_cover_with_fixtures(fixture_art, tmp_path):
    interior = tmp_path / "interior.pdf"
    cover = tmp_path / "cover.pdf"
    Composer().write_interior(interior)
    CoverComposer().write(cover)
    reader = PdfReader(str(interior))
    assert len(reader.pages) == 48
    box = reader.pages[0].mediabox
    assert abs(float(box.width) / 72 - 8.5) < 0.01
    assert abs(float(box.height) / 72 - 11.0) < 0.01
    cover_reader = PdfReader(str(cover))
    assert len(cover_reader.pages) == 1
    # Fixture art must not leak into the production accepted folder.
    leaked = list(ASSETS_ACCEPTED.glob("*.jpg")) + list(ASSETS_ACCEPTED.glob("*.png"))
    assert leaked == []
