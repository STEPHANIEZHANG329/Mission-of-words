"""Append-only asset provenance ledger for Phase C paid artwork.

The committed file `ops/asset_ledger.json` is the source of truth for
`paid_image_calls` so a later CI run cannot silently re-spend lost images.
`output/asset_ledger.json` is a working copy written during a run.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mission_of_words.paths import OPS_DIR, OUTPUT_DIR

CANONICAL_LEDGER = OPS_DIR / "asset_ledger.json"
LEDGER_JSON = OUTPUT_DIR / "asset_ledger.json"
LEDGER_JSONL = OPS_DIR / "asset_ledger.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_ledger() -> dict[str, Any]:
    return {
        "kind": "bright_hearts_asset_ledger",
        "max_paid_image_calls": 24,
        "paid_image_calls": 0,
        "estimated_spend_usd": 0.0,
        "assets": [],
    }


def _default_ledger_path() -> Path:
    if CANONICAL_LEDGER.is_file():
        return CANONICAL_LEDGER
    return LEDGER_JSON


def load_ledger(path: Path | None = None) -> dict[str, Any]:
    ledger_path = path or _default_ledger_path()
    if ledger_path.is_file():
        return json.loads(ledger_path.read_text(encoding="utf-8"))
    return _empty_ledger()


def write_ledger(ledger: dict[str, Any], *, path: Path | None = None) -> Path:
    dest = path or CANONICAL_LEDGER
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    if dest.resolve() == CANONICAL_LEDGER.resolve():
        LEDGER_JSON.parent.mkdir(parents=True, exist_ok=True)
        LEDGER_JSON.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    return dest


def paid_image_calls(ledger: dict[str, Any] | None = None) -> int:
    record = ledger if ledger is not None else load_ledger()
    return int(record.get("paid_image_calls") or 0)


def billed_asset_ids(ledger: dict[str, Any] | None = None) -> set[str]:
    record = ledger if ledger is not None else load_ledger()
    return {
        str(item["asset_id"])
        for item in record.get("assets") or []
        if item.get("asset_id") and item.get("paid_call")
    }


def append_asset(row: dict[str, Any], *, path: Path | None = None) -> dict[str, Any]:
    ledger_path = path or CANONICAL_LEDGER
    ledger = load_ledger(ledger_path)
    payload = dict(row)
    payload.setdefault("ts", _now())
    ledger.setdefault("assets", []).append(payload)
    if payload.get("paid_call"):
        ledger["paid_image_calls"] = int(ledger.get("paid_image_calls") or 0) + 1
        ledger["estimated_spend_usd"] = round(
            float(ledger.get("estimated_spend_usd") or 0) + float(payload.get("estimated_usd") or 0),
            2,
        )
    write_ledger(ledger, path=ledger_path)
    if path is None or ledger_path.resolve() == CANONICAL_LEDGER.resolve():
        LEDGER_JSONL.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return ledger


def remaining_calls(ledger: dict[str, Any] | None = None, cap: int | None = None) -> int:
    """Cumulative remaining spend. Owner-stop and the gate file win over any cap argument."""
    gate_path = OPS_DIR / "phase_c_paid_gate.json"
    gate: dict[str, Any] = {}
    if gate_path.is_file():
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
    if gate.get("owner_stop"):
        return 0
    if "remaining_calls" in gate:
        return max(0, int(gate.get("remaining_calls") or 0))
    if cap is None:
        cap = int(gate.get("max_paid_calls") or 24)
    return max(0, int(cap) - paid_image_calls(ledger))


def asset_by_id(asset_id: str, ledger: dict[str, Any] | None = None) -> dict[str, Any] | None:
    record = ledger if ledger is not None else load_ledger()
    for item in reversed(list(record.get("assets") or [])):
        if item.get("asset_id") == asset_id:
            return item
    return None
