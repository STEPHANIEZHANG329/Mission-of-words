"""Source-locked Bible records. Refuse missing or empty canon; never invent facts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mission_of_words.paths import CANON_DIR


class CanonError(ValueError):
    """Raised when a canon record is missing, empty, or inconsistent."""


def canon_path(canon_id: str) -> Path:
    if not canon_id or not isinstance(canon_id, str):
        raise CanonError("canon_id is required")
    if "/" in canon_id or "\\" in canon_id or ".." in canon_id:
        raise CanonError(f"invalid canon_id: {canon_id!r}")
    return CANON_DIR / f"{canon_id}.json"


def load_canon(canon_id: str, *, canon_dir: Path | None = None) -> dict[str, Any]:
    """Load one source-locked canon record. Fail closed on any defect."""
    directory = canon_dir or CANON_DIR
    if not canon_id or not isinstance(canon_id, str):
        raise CanonError("missing canon_id")
    if "/" in canon_id or "\\" in canon_id or ".." in canon_id:
        raise CanonError(f"invalid canon_id: {canon_id!r}")

    path = directory / f"{canon_id}.json"
    if not path.is_file():
        raise CanonError(f"missing canon record: {canon_id}")

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CanonError(f"canon record is not valid JSON: {canon_id}") from exc

    if not isinstance(record, dict):
        raise CanonError(f"canon record must be an object: {canon_id}")

    if record.get("canon_id") != canon_id:
        raise CanonError(
            f"canon_id mismatch: file {canon_id} declares {record.get('canon_id')!r}"
        )

    source_text = record.get("source_text")
    if not isinstance(source_text, str) or not source_text.strip():
        raise CanonError(f"canon {canon_id} has empty source_text")

    reference = record.get("reference")
    if not isinstance(reference, str) or not reference.strip():
        raise CanonError(f"canon {canon_id} has empty reference")

    paraphrase = record.get("child_paraphrase")
    if paraphrase is not None and not isinstance(paraphrase, str):
        raise CanonError(f"canon {canon_id} child_paraphrase must be a string")

    if isinstance(paraphrase, str) and paraphrase.strip() == source_text.strip():
        raise CanonError(
            f"canon {canon_id} mixes paraphrase into source_text; keep them separate"
        )

    return record


def bind_mission_canon(spec: dict[str, Any], *, canon_dir: Path | None = None) -> dict[str, Any]:
    """Return the canon record required by a mission spec, or fail closed."""
    mission = spec.get("mission") if isinstance(spec, dict) else None
    if not isinstance(mission, dict):
        raise CanonError("mission spec is missing")
    return bind_canon_id(
        mission.get("canon_id"),
        scripture_reference=mission.get("scripture_reference"),
        canon_dir=canon_dir,
    )


def bind_canon_id(
    canon_id: Any,
    *,
    scripture_reference: Any = None,
    canon_dir: Path | None = None,
) -> dict[str, Any]:
    if not canon_id:
        raise CanonError("mission is missing canon_id")
    record = load_canon(str(canon_id), canon_dir=canon_dir)
    if scripture_reference and scripture_reference != record["reference"]:
        raise CanonError(
            "mission scripture_reference does not match canon reference: "
            f"{scripture_reference!r} != {record['reference']!r}"
        )
    return record


def bind_mission_record(mission: dict[str, Any], *, canon_dir: Path | None = None) -> dict[str, Any]:
    if not isinstance(mission, dict):
        raise CanonError("mission record is missing")
    return bind_canon_id(
        mission.get("canon_id"),
        scripture_reference=mission.get("scripture_reference"),
        canon_dir=canon_dir,
    )


def list_canon_ids(canon_dir: Path | None = None) -> list[str]:
    directory = canon_dir or CANON_DIR
    return sorted(path.stem for path in directory.glob("*.json"))


def load_all_canons(*, canon_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for canon_id in list_canon_ids(canon_dir):
        records[canon_id] = load_canon(canon_id, canon_dir=canon_dir)
    return records
