"""Raw / accepted / rejected asset store with provenance validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mission_of_words.paths import ASSETS_DIR

STATUSES = ("raw", "accepted", "rejected")
SKIP_NAMES = {".gitkeep", ".gitignore"}
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".pdf", ".svg"}


class AssetStoreError(ValueError):
    """Raised when the asset store or provenance records are inconsistent."""


def asset_dirs(root: Path | None = None) -> dict[str, Path]:
    base = root or ASSETS_DIR
    return {
        "raw": base / "raw",
        "accepted": base / "accepted",
        "rejected": base / "rejected",
        "provenance": base / "provenance",
    }


def ensure_store(root: Path | None = None) -> dict[str, Path]:
    dirs = asset_dirs(root)
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _asset_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    files = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name in SKIP_NAMES:
            continue
        if path.suffix.lower() not in ASSET_SUFFIXES:
            continue
        files.append(path)
    return files


def validate_store(root: Path | None = None) -> list[str]:
    """Return human-readable defects. Empty list means the store is valid."""
    dirs = asset_dirs(root)
    errors: list[str] = []
    for name, path in dirs.items():
        if not path.is_dir():
            errors.append(f"missing asset directory: assets/{name}")
    if errors:
        return errors

    seen_ids: dict[str, str] = {}
    for status in STATUSES:
        for asset in _asset_files(dirs[status]):
            asset_id = asset.stem
            if asset_id in seen_ids:
                errors.append(
                    f"asset_id {asset_id} appears in both {seen_ids[asset_id]} and {status}"
                )
            seen_ids[asset_id] = status
            provenance_path = dirs["provenance"] / f"{asset_id}.json"
            if not provenance_path.is_file():
                errors.append(f"missing provenance for {status}/{asset.name}")
                continue
            try:
                record = json.loads(provenance_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"provenance is not valid JSON: {asset_id}")
                continue
            if not isinstance(record, dict):
                errors.append(f"provenance must be an object: {asset_id}")
                continue
            if record.get("asset_id") not in {None, asset_id} and record.get("asset_id") != asset_id:
                errors.append(f"provenance asset_id mismatch: {asset_id}")
            if record.get("status") != status:
                errors.append(
                    f"provenance status {record.get('status')!r} does not match folder {status} for {asset_id}"
                )
            expected_sha = record.get("sha256")
            if expected_sha:
                actual = _sha256(asset)
                if actual != expected_sha:
                    errors.append(f"sha256 mismatch for {asset_id}")
            if record.get("paid_call") is True:
                errors.append(f"paid_call is true on {asset_id}; V1 store must stay unpaid")
    return errors


def load_provenance(asset_id: str, root: Path | None = None) -> dict[str, Any]:
    path = asset_dirs(root)["provenance"] / f"{asset_id}.json"
    if not path.is_file():
        raise AssetStoreError(f"missing provenance: {asset_id}")
    return json.loads(path.read_text(encoding="utf-8"))


REQUIRED_SEARCH_TARGET_NAMES = {
    "lantern",
    "pumpkin",
    "apple",
    "leaf",
    "acorn",
    "scarf",
    "basket",
    "Bible",
}


def accepted_artwork_inventory(root: Path | None = None) -> dict[str, Any]:
    """Return whether required accepted artwork exists. Empty store is valid but incomplete."""
    dirs = asset_dirs(root)
    accepted = dirs["accepted"]
    provenance_dir = dirs["provenance"]
    roles: dict[str, list[str]] = {}
    names: set[str] = set()
    if accepted.is_dir():
        for asset in _asset_files(accepted):
            record: dict[str, Any] = {}
            provenance_path = provenance_dir / f"{asset.stem}.json"
            if provenance_path.is_file():
                try:
                    loaded = json.loads(provenance_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        record = loaded
                except json.JSONDecodeError:
                    record = {}
            role = str(record.get("role") or "other")
            roles.setdefault(role, []).append(asset.stem)
            if record.get("name"):
                names.add(str(record["name"]))
            elif role == "search_target":
                names.add(asset.stem)
    missing: list[str] = []
    if not roles.get("coloring_background"):
        missing.append("accepted coloring_background")
    if not roles.get("search_background"):
        missing.append("accepted search_background")
    found_targets = names & REQUIRED_SEARCH_TARGET_NAMES
    if found_targets != REQUIRED_SEARCH_TARGET_NAMES:
        missing.append(
            "accepted search_target assets for "
            + ", ".join(sorted(REQUIRED_SEARCH_TARGET_NAMES - found_targets))
        )
    return {
        "complete": not missing,
        "missing": missing,
        "roles": roles,
        "search_target_names": sorted(found_targets),
    }
