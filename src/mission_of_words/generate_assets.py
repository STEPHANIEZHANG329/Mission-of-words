"""Bounded GPT2 generation: planned packets only, no hidden retries.

Assets already billed in the committed ledger are never requested again,
even if the PNG files were lost. That keeps a failed artifact upload from
silently doubling Owner spend against the 24-call cap.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mission_of_words.asset_ledger import (
    billed_asset_ids,
    append_asset,
    load_ledger,
    remaining_calls,
    write_ledger,
)
from mission_of_words.paid_images import (
    CONFIRM_PHRASE,
    FALLBACK_SIZE,
    INTERIOR_MODEL,
    PaidImageError,
    generate_png,
    generation_authorized,
    max_paid_calls,
)
from mission_of_words.paths import ASSETS_DIR, OUTPUT_DIR, ROOT
from mission_of_words.prompt_packets import planned_packets, write_prompt_packets

RAW_DIR = ASSETS_DIR / "raw"
ACCEPTED_DIR = ASSETS_DIR / "accepted"


def _dest_for(packet: dict, raw_dir: Path) -> Path:
    return raw_dir / f"{packet['asset_id']}.png"


def generate_planned(
    *,
    confirm: str,
    accept_all: bool = True,
    ledger_path: Path | None = None,
    raw_dir: Path | None = None,
    accepted_dir: Path | None = None,
) -> dict:
    ok, reason = generation_authorized(confirm=confirm)
    if not ok:
        raise PaidImageError(reason)
    write_prompt_packets()
    packets = planned_packets()
    ledger = load_ledger(ledger_path)
    cap = max_paid_calls()
    raw = raw_dir or RAW_DIR
    accepted_root = accepted_dir or ACCEPTED_DIR
    billed = billed_asset_ids(ledger)
    summary: dict = {
        "generated": [],
        "skipped": [],
        "failed": [],
        "missing_after_paid_call": [],
        "paid_image_calls": ledger.get("paid_image_calls", 0),
        "remaining_calls": remaining_calls(ledger, cap=cap),
        "new_paid_calls": 0,
    }
    accepted_root.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)

    for packet in packets:
        dest = _dest_for(packet, raw)
        accepted = accepted_root / dest.name
        asset_id = packet["asset_id"]
        if accepted.is_file() or dest.is_file():
            summary["skipped"].append(asset_id)
            continue
        if asset_id in billed:
            summary["skipped"].append(asset_id)
            summary["missing_after_paid_call"].append(asset_id)
            continue
        left = remaining_calls(load_ledger(ledger_path), cap=cap)
        if left <= 0:
            summary["failed"].append({"asset_id": asset_id, "error": "cap reached"})
            break
        try:
            row = generate_png(
                prompt=packet["prompt"],
                dest=dest,
                asset_id=asset_id,
                role=packet["role"],
                model=packet.get("model") or INTERIOR_MODEL,
                remaining_calls=left,
            )
            if accept_all:
                accepted.write_bytes(dest.read_bytes())
                row["accepted"] = True
                row["status"] = "accepted"
                try:
                    row["accepted_path"] = str(accepted.relative_to(ROOT))
                except ValueError:
                    row["accepted_path"] = str(accepted)
            append_asset(row, path=ledger_path)
            summary["generated"].append(asset_id)
            summary["new_paid_calls"] = int(summary["new_paid_calls"]) + 1
        except PaidImageError as exc:
            append_asset(
                {
                    "asset_id": asset_id,
                    "role": packet["role"],
                    "status": "rejected",
                    "accepted": False,
                    "paid_call": True,
                    "error": str(exc)[:400],
                    "model": packet.get("model"),
                    "size": packet.get("size") or FALLBACK_SIZE,
                },
                path=ledger_path,
            )
            summary["failed"].append({"asset_id": asset_id, "error": str(exc)[:400]})
            # No hidden retry. Stop the loop only if the cap is exhausted.
    ledger = load_ledger(ledger_path)
    write_ledger(ledger, path=ledger_path)
    summary["paid_image_calls"] = ledger.get("paid_image_calls", 0)
    summary["estimated_spend_usd"] = ledger.get("estimated_spend_usd", 0)
    summary["remaining_calls"] = remaining_calls(ledger, cap=cap)
    if summary["missing_after_paid_call"]:
        summary["blocker"] = (
            "Paid PNGs are missing for already-billed asset ids. "
            "Do not regenerate them unless the Owner raises the 24-call cap. "
            f"remaining_calls={summary['remaining_calls']}."
        )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "generation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", required=True)
    parser.add_argument("--accept-all", action="store_true", default=True)
    args = parser.parse_args()
    if args.confirm != CONFIRM_PHRASE:
        raise SystemExit("confirm phrase does not match")
    summary = generate_planned(confirm=args.confirm, accept_all=True)
    print(json.dumps({k: summary[k] for k in summary if k != "packets"}, indent=2))
    if summary["failed"] and not summary["generated"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
