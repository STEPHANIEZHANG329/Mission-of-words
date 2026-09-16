import json
from pathlib import Path

from PIL import Image

from mission_of_words.assets import ensure_store, validate_store
from mission_of_words.paths import ASSETS_DIR


def test_repo_asset_store_is_present_and_empty_of_paid_files():
    errors = validate_store()
    assert errors == []
    for name in ("raw", "accepted", "rejected", "provenance"):
        assert (ASSETS_DIR / name).is_dir()


def test_asset_without_provenance_fails(tmp_path: Path):
    dirs = ensure_store(tmp_path)
    Image.new("RGB", (8, 8), "white").save(dirs["raw"] / "lantern.png")
    errors = validate_store(tmp_path)
    assert any("missing provenance" in item for item in errors)


def test_accepted_asset_with_matching_provenance_passes(tmp_path: Path):
    dirs = ensure_store(tmp_path)
    asset = dirs["accepted"] / "as_lantern_v1.png"
    Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(asset)
    sha = __import__("hashlib").sha256(asset.read_bytes()).hexdigest()
    (dirs["provenance"] / "as_lantern_v1.json").write_text(
        json.dumps(
            {
                "asset_id": "as_lantern_v1",
                "role": "search_target",
                "status": "accepted",
                "request_id": "dry-run",
                "model": None,
                "prompt": None,
                "file": "assets/accepted/as_lantern_v1.png",
                "sha256": sha,
                "cost_usd": 0.0,
                "attempts": 0,
                "paid_call": False,
            }
        ),
        encoding="utf-8",
    )
    assert validate_store(tmp_path) == []


def test_paid_call_flag_on_asset_fails(tmp_path: Path):
    dirs = ensure_store(tmp_path)
    asset = dirs["raw"] / "secret.png"
    Image.new("RGB", (4, 4), "white").save(asset)
    (dirs["provenance"] / "secret.json").write_text(
        json.dumps(
            {
                "asset_id": "secret",
                "status": "raw",
                "paid_call": True,
                "sha256": None,
            }
        ),
        encoding="utf-8",
    )
    errors = validate_store(tmp_path)
    assert any("paid_call is true" in item for item in errors)
