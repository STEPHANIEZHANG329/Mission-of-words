"""Owner-gated budget and append-only paid-call ledger. V1 keeps spend at zero."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mission_of_words.paths import BUDGET_PATH, LEDGER_PATH


class BudgetError(ValueError):
    """Raised when budget policy forbids a paid call."""


def load_budget(path: Path | None = None) -> dict[str, Any]:
    budget_path = path or BUDGET_PATH
    if not budget_path.is_file():
        raise BudgetError(f"missing budget file: {budget_path}")
    budget = json.loads(budget_path.read_text(encoding="utf-8"))
    if not isinstance(budget, dict):
        raise BudgetError("budget.json must be an object")
    return budget


def paid_calls_disabled(budget: dict[str, Any] | None = None) -> bool:
    record = budget if budget is not None else load_budget()
    enabled = bool(record.get("paid_calls_enabled"))
    allow = bool(record.get("allow_paid_image_calls"))
    max_calls = int(record.get("max_paid_calls", 0) or 0)
    max_usd = float(record.get("max_usd", 0) or 0)
    return (not enabled) or (not allow) or max_calls <= 0 or max_usd <= 0


def assert_paid_call_forbidden(
    *,
    estimated_usd: float = 0.0,
    budget_path: Path | None = None,
    gate_implemented: bool = False,
) -> None:
    """Fail closed. V1 never authorizes a paid image call."""
    budget = load_budget(budget_path)
    reasons: list[str] = []
    if not gate_implemented:
        reasons.append("owner-approved paid-image gate is not implemented")
    if not budget.get("paid_calls_enabled"):
        reasons.append("paid_calls_enabled is false")
    if not budget.get("allow_paid_image_calls"):
        reasons.append("allow_paid_image_calls is false")
    max_calls = int(budget.get("max_paid_calls", 0) or 0)
    spent_calls = int(budget.get("spent_calls", 0) or 0)
    max_usd = float(budget.get("max_usd", 0) or 0)
    spent_usd = float(budget.get("spent_usd", 0) or 0)
    if max_calls <= 0 or spent_calls + 1 > max_calls:
        reasons.append("max_paid_calls would be exceeded")
    if max_usd <= 0 or spent_usd + float(estimated_usd) > max_usd:
        reasons.append("max_usd would be exceeded")
    raise BudgetError(
        "Paid image generation is disabled. No network call was made. "
        + "; ".join(reasons)
    )


def append_ledger(row: dict[str, Any], path: Path | None = None) -> None:
    """Append one JSON line. Never rewrite existing ledger rows."""
    ledger_path = path or LEDGER_PATH
    payload = dict(row)
    payload.setdefault("ts", datetime.now(timezone.utc).isoformat())
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def read_ledger(path: Path | None = None) -> list[dict[str, Any]]:
    ledger_path = path or LEDGER_PATH
    if not ledger_path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows
