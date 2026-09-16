"""Accepted-asset ingestion. Technical proof stays on the procedural path."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from mission_of_words.assets import asset_dirs, validate_store
from mission_of_words.layout import DPI
from mission_of_words.paths import ASSETS_DIR
from mission_of_words.production_assets import load_production_manifest

MIN_ACCEPTED_PX = 512


class IngestError(ValueError):
    """Raised when an accepted production asset cannot be used."""


@dataclass(frozen=True)
class AcceptedAsset:
    asset_id: str
    role: str
    path: Path
    provenance: dict[str, Any]
    width: int
    height: int
    sha256: str


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def overlay_manifest_with_store(
    *,
    manifest: dict[str, Any] | None = None,
    store_root: Path | None = None,
) -> dict[str, Any]:
    """Return a copy of the production manifest with store statuses applied."""
    record = json.loads(json.dumps(manifest or load_production_manifest()))
    dirs = asset_dirs(store_root)
    accepted_dir = dirs["accepted"]
    provenance_dir = dirs["provenance"]
    for asset in record["assets"]:
        asset_id = asset["asset_id"]
        provenence_path = provenance_dir / f"{asset_id}.json"
        matches = list(accepted_dir.glob(f"{asset_id}.*")) if accepted_dir.is_dir() else []
        matches = [path for path in matches if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".webp"}]
        if not matches or not provenence_path.is_file():
            continue
        provenance = _read_json(provenence_path)
        if provenance.get("status") != "accepted":
            continue
        asset["status"] = "accepted"
        asset["accepted"] = True
        asset["rejected"] = False
        asset["file"] = str(matches[0])
        asset["final_file_hash"] = provenance.get("sha256")
        asset["provider"] = provenance.get("provider") or provenance.get("model")
        asset["model"] = provenance.get("model")
        asset["cost_usd"] = float(provenance.get("cost_usd") or 0)
        asset["attempt"] = int(provenance.get("attempts") or provenance.get("attempt") or 0)
        asset["rejection_reason"] = None
    return record


def load_accepted_asset(asset_id: str, store_root: Path | None = None) -> AcceptedAsset:
    dirs = asset_dirs(store_root)
    matches = [
        path
        for path in dirs["accepted"].glob(f"{asset_id}.*")
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".webp"}
    ]
    if not matches:
        raise IngestError(f"missing accepted file for {asset_id}")
    path = matches[0]
    provenance_path = dirs["provenance"] / f"{asset_id}.json"
    if not provenance_path.is_file():
        raise IngestError(f"missing provenance for accepted asset {asset_id}")
    provenance = _read_json(provenance_path)
    if provenance.get("status") != "accepted":
        raise IngestError(f"{asset_id} provenance status is {provenance.get('status')!r}, not accepted")
    with Image.open(path) as image:
        width, height = image.size
    if min(width, height) < MIN_ACCEPTED_PX:
        raise IngestError(f"{asset_id} is {width}x{height}, below {MIN_ACCEPTED_PX}px")
    effective_dpi = min(width, height)  # compared against layout at compose time
    if effective_dpi < MIN_ACCEPTED_PX:
        raise IngestError(f"{asset_id} failed minimum pixel floor")
    sha = str(provenance.get("sha256") or "")
    return AcceptedAsset(
        asset_id=asset_id,
        role=str(provenance.get("role") or ""),
        path=path,
        provenance=provenance,
        width=width,
        height=height,
        sha256=sha,
    )


def missing_accepted_assets(
    *,
    manifest: dict[str, Any] | None = None,
    store_root: Path | None = None,
) -> list[str]:
    record = overlay_manifest_with_store(manifest=manifest, store_root=store_root)
    missing: list[str] = []
    for asset in record["assets"]:
        if not asset.get("needs_ai_art"):
            continue
        if asset.get("status") != "accepted" or not asset.get("accepted"):
            missing.append(str(asset["asset_id"]))
    return missing


def ingest_failures(
    *,
    manifest: dict[str, Any] | None = None,
    store_root: Path | None = None,
) -> list[str]:
    errors = validate_store(store_root or ASSETS_DIR)
    record = overlay_manifest_with_store(manifest=manifest, store_root=store_root)
    for asset_id in missing_accepted_assets(manifest=record, store_root=store_root):
        errors.append(f"production asset {asset_id} is not accepted")
    for asset in record["assets"]:
        if asset.get("status") != "accepted":
            continue
        try:
            loaded = load_accepted_asset(asset["asset_id"], store_root)
        except IngestError as exc:
            errors.append(str(exc))
            continue
        if loaded.width < asset["width_px"] * 0.5 or loaded.height < asset["height_px"] * 0.5:
            errors.append(
                f"{asset['asset_id']} accepted raster {loaded.width}x{loaded.height} "
                f"is too small for slot {asset['width_px']}x{asset['height_px']}"
            )
        if int(asset.get("dpi") or 0) != DPI:
            errors.append(f"{asset['asset_id']} dpi must be {DPI}")
    return errors


def search_kit(mission_id: str, store_root: Path | None = None) -> dict[str, Any]:
    record = overlay_manifest_with_store(store_root=store_root)
    background = None
    targets: dict[str, AcceptedAsset] = {}
    for asset in record["assets"]:
        if asset.get("mission_id") != mission_id:
            continue
        if asset.get("status") != "accepted":
            continue
        loaded = load_accepted_asset(asset["asset_id"], store_root)
        if asset["role"] == "search_background":
            background = loaded
        elif asset["role"] == "search_target":
            targets[str(asset.get("target_name"))] = loaded
    if background is None or len(targets) != 8:
        raise IngestError(
            f"{mission_id} accepted search kit is incomplete "
            f"(background={background is not None}, targets={len(targets)})"
        )
    return {"background": background, "targets": targets}
