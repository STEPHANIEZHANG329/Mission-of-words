"""Append-only asset provenance ledger for Phase C paid artwork."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mission_of_words.paths import OUTPUT_DIR, ROOT

LEDGER_JSON = OUTPUT_DIR / "asset_ledger.json"
LEDGER_JSONL = ROOT / "ops" / "asset_ledger.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_ledger(path: Path | None = None) -> dict[str, Any]:
    ledger_path = path or LEDGER_JSON
    if ledger_path.is_file():
        return json.loads(ledger_path.read_text(encoding="utf-8"))
    return {
        "kind": "bright_hearts_asset_ledger",
        "max_paid_image_calls": 24,
        "paid_image_calls": 0,
        "estimated_spend_usd": 0.0,
        "assets": [],
    }


def paid_image_calls(ledger: dict[str, Any] | None = None) -> int:
    record = ledger if ledger is not None else load_ledger()
    return int(record.get("paid_image_calls") or 0)


def append_asset(row: dict[str, Any], *, path: Path | None = None) -> dict[str, Any]:
    ledger_path = path or LEDGER_JSON
    ledger = load_ledger(ledger_path)
    payload = dict(row)
    payload.setdefault("ts", _now())
    ledger.setdefault("assets", []).append(payload)
    if payload.get("paid_call"):
        ledger["paid_image_calls"] = int(ledger.get("paid_image_calls") or 0) + 1
        ledger["estimated_spend_usd"] = float(ledger.get("estimated_spend_usd") or 0) + float(
            payload.get("estimated_usd") or 0
        )
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    LEDGER_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return ledger


def remaining_calls(ledger: dict[str, Any] | None = None, cap: int = 24) -> int:
    return max(0, cap - paid_image_calls(ledger))


def asset_by_id(asset_id: str, ledger: dict[str, Any] | None = None) -> dict[str, Any] | None:
    record = ledger if ledger is not None else load_ledger()
    for item in reversed(list(record.get("assets") or [])):
        if item.get("asset_id") == asset_id:
            return item
    return None
