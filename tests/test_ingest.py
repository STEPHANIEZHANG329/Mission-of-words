import hashlib
import json
from pathlib import Path

from PIL import Image

from mission_of_words.assets import ensure_store
from mission_of_words.ingest import (
    IngestError,
    ingest_failures,
    load_accepted_asset,
    missing_accepted_assets,
    overlay_manifest_with_store,
)
from mission_of_words.page_coloring import draw_mission_coloring_page
from mission_of_words.page_search import build_search_scene_from_page
from mission_of_words.book_manifest import load_mission_records
from mission_of_words.production_assets import load_production_manifest
from reportlab.pdfgen import canvas


def _write_accepted(dirs: dict[str, Path], asset_id: str, role: str, size: int = 1024) -> Path:
    path = dirs["accepted"] / f"{asset_id}.png"
    Image.new("RGBA", (size, size), (255, 255, 255, 0)).save(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    (dirs["provenance"] / f"{asset_id}.json").write_text(
        json.dumps(
            {
                "asset_id": asset_id,
                "role": role,
                "status": "accepted",
                "request_id": "test",
                "model": None,
                "prompt": None,
                "file": str(path),
                "sha256": sha,
                "cost_usd": 0.0,
                "attempts": 1,
                "paid_call": False,
            }
        ),
        encoding="utf-8",
    )
    return path


def test_missing_accepted_assets_lists_every_required_slot():
    missing = missing_accepted_assets()
    assert len(missing) == 136


def test_ingest_loads_matching_accepted_file(tmp_path: Path):
    dirs = ensure_store(tmp_path)
    _write_accepted(dirs, "demo_hero", "coloring_hero")
    loaded = load_accepted_asset("demo_hero", tmp_path)
    assert loaded.width == 1024
    assert loaded.role == "coloring_hero"


def test_ingest_rejects_tiny_accepted_file(tmp_path: Path):
    dirs = ensure_store(tmp_path)
    _write_accepted(dirs, "tiny_hero", "coloring_hero", size=64)
    try:
        load_accepted_asset("tiny_hero", tmp_path)
    except IngestError as exc:
        assert "below" in str(exc)
    else:
        raise AssertionError("expected IngestError")


def test_overlay_marks_store_assets_accepted(tmp_path: Path):
    dirs = ensure_store(tmp_path)
    manifest = load_production_manifest()
    first = manifest["assets"][0]["asset_id"]
    role = manifest["assets"][0]["role"]
    _write_accepted(dirs, first, role)
    overlaid = overlay_manifest_with_store(manifest=manifest, store_root=tmp_path)
    row = next(asset for asset in overlaid["assets"] if asset["asset_id"] == first)
    assert row["status"] == "accepted"
    assert row["accepted"] is True
    assert ingest_failures(manifest=overlaid, store_root=tmp_path)


def test_coloring_page_ingests_accepted_raster(tmp_path: Path):
    mission = load_mission_records()[0]
    image = tmp_path / "hero.png"
    Image.new("RGB", (1200, 1600), "white").save(image)
    pdf = tmp_path / "page.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(612, 792))
    record = draw_mission_coloring_page(
        c,
        mission,
        {"reference": "Matthew 5:16"},
        page_number=5,
        marked_proof=False,
        accepted_image=image,
    )
    c.save()
    assert record["artwork_status"] == "accepted"
    assert record["placeholder"] is False


def test_accepted_search_kit_composes(tmp_path: Path):
    mission = load_mission_records()[0]
    dirs = ensure_store(tmp_path)
    manifest = load_production_manifest()
    for asset in manifest["assets"]:
        if asset.get("mission_id") != mission["id"]:
            continue
        if asset["role"] not in {"search_background", "search_target"}:
            continue
        _write_accepted(dirs, asset["asset_id"], asset["role"], size=1024)
    dest = tmp_path / "scene"
    composed, search_manifest, records = build_search_scene_from_page(
        mission["pages"][1],
        dest,
        page_number=6,
        theme=mission["id"],
        marked_proof=False,
        source="accepted",
        store_root=tmp_path,
    )
    assert composed.is_file()
    assert len(search_manifest) == 8
    assert all(record["status"] == "accepted" for record in records)
