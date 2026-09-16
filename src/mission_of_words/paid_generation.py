"""Manual paid-generation workflow. Disabled by default. Fail closed.

Ordinary PR CI must never import a vendor SDK or open a network connection
through this module. generate() always refuses unless every owner gate is
present, and even then this pass keeps the HTTP client unimplemented.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from mission_of_words.budget import BudgetError, assert_paid_call_forbidden, load_budget, paid_calls_disabled
from mission_of_words.image_client import (
    PAID_GENERATION_GATE_IMPLEMENTED,
    PaidGenerationDisabled,
    dry_run_info,
    generate_image,
    paid_call_count,
)
from mission_of_words.production_assets import load_production_manifest, role_counts

CONFIRM_PHRASE = "OWNER_APPROVES_PAID_IMAGE_GENERATION"
# Explicit owner phrase plus budget caps are required. Flipping this comment
# is not an authorization to spend.
WORKFLOW_ENABLED_BY_DEFAULT = False


class PaidGenerationRefused(RuntimeError):
    """Raised when the manual paid-generation workflow refuses to spend."""


def env_allows_paid_calls() -> bool:
    return os.environ.get("ALLOW_PAID_IMAGE_CALLS") == "1"


def workflow_gates(
    *,
    approved_budget_usd: float = 0.0,
    call_cap: int = 0,
    confirm_phrase: str = "",
    estimated_usd: float = 0.04,
) -> list[str]:
    reasons: list[str] = []
    if WORKFLOW_ENABLED_BY_DEFAULT:
        reasons.append("manual workflow is enabled by default; it must stay disabled")
    if not PAID_GENERATION_GATE_IMPLEMENTED:
        reasons.append("owner-approved paid-image gate is not implemented")
    if not env_allows_paid_calls():
        reasons.append("ALLOW_PAID_IMAGE_CALLS is not exactly 1")
    if confirm_phrase != CONFIRM_PHRASE:
        reasons.append("confirm phrase does not match OWNER_APPROVES_PAID_IMAGE_GENERATION")
    if float(approved_budget_usd) <= 0:
        reasons.append("approved_budget_usd must be > 0")
    if int(call_cap) <= 0:
        reasons.append("call_cap must be > 0")
    try:
        budget = load_budget()
    except BudgetError as exc:
        reasons.append(str(exc))
        return reasons
    if paid_calls_disabled(budget):
        reasons.append("ops/budget.json keeps paid calls disabled")
    if float(approved_budget_usd) > float(budget.get("max_usd") or 0):
        reasons.append("approved_budget_usd exceeds budget.json max_usd")
    if int(call_cap) > int(budget.get("max_paid_calls") or 0):
        reasons.append("call_cap exceeds budget.json max_paid_calls")
    try:
        assert_paid_call_forbidden(
            estimated_usd=estimated_usd,
            gate_implemented=PAID_GENERATION_GATE_IMPLEMENTED,
        )
    except BudgetError as exc:
        reasons.append(str(exc))
    return reasons


def run_manual_generation(
    *,
    asset_ids: list[str] | None = None,
    approved_budget_usd: float = 0.0,
    call_cap: int = 0,
    confirm_phrase: str = "",
) -> dict[str, Any]:
    """Refuse paid generation. Never opens a network connection."""
    reasons = workflow_gates(
        approved_budget_usd=approved_budget_usd,
        call_cap=call_cap,
        confirm_phrase=confirm_phrase,
    )
    manifest = load_production_manifest()
    wanted = list(asset_ids or [asset["asset_id"] for asset in manifest["assets"]])
    report = {
        "mode": "manual_paid_generation",
        "enabled_by_default": WORKFLOW_ENABLED_BY_DEFAULT,
        "paid_generation_gate_implemented": PAID_GENERATION_GATE_IMPLEMENTED,
        "dry_run": dry_run_info(),
        "requested_asset_ids": wanted,
        "requested_count": len(wanted),
        "role_counts": role_counts(manifest),
        "paid_image_calls": paid_call_count(),
        "refused": True,
        "reasons": reasons,
        "network_allowed": False,
    }
    if reasons:
        raise PaidGenerationRefused(
            "Paid image generation is disabled. No network call was made. " + "; ".join(reasons)
        )
    # Even if every owner gate were later opened, this pass still has no HTTP
    # client. generate_image remains dry-run and will refuse.
    try:
        generate_image(prompt="refused", role="other", estimated_usd=0.04)
    except PaidGenerationDisabled as exc:
        raise PaidGenerationRefused(str(exc)) from exc
    raise PaidGenerationRefused("Paid image generation is disabled. No network call was made.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manual paid image generation (disabled by default).")
    parser.add_argument("--approved-budget-usd", type=float, default=0.0)
    parser.add_argument("--call-cap", type=int, default=0)
    parser.add_argument("--confirm-phrase", default="")
    parser.add_argument("--asset-id", action="append", dest="asset_ids")
    args = parser.parse_args(argv)
    try:
        run_manual_generation(
            asset_ids=args.asset_ids,
            approved_budget_usd=args.approved_budget_usd,
            call_cap=args.call_cap,
            confirm_phrase=args.confirm_phrase,
        )
    except PaidGenerationRefused as exc:
        print(json.dumps({"ok": False, "paid_image_calls": paid_call_count(), "error": str(exc)}, indent=2))
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
