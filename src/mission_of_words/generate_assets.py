"""Bounded GPT2 generation: planned packets only, no hidden retries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mission_of_words.asset_ledger import LEDGER_JSON, append_asset, load_ledger, remaining_calls
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


def _dest_for(packet: dict) -> Path:
    return RAW_DIR / f"{packet['asset_id']}.png"


def generate_planned(*, confirm: str, accept_all: bool = True) -> dict:
    ok, reason = generation_authorized(confirm=confirm)
    if not ok:
        raise PaidImageError(reason)
    write_prompt_packets()
    packets = planned_packets()
    ledger = load_ledger()
    cap = max_paid_calls()
    summary = {"generated": [], "skipped": [], "failed": [], "paid_image_calls": ledger.get("paid_image_calls", 0)}
    ACCEPTED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for packet in packets:
        dest = _dest_for(packet)
        accepted = ACCEPTED_DIR / dest.name
        if accepted.is_file() or dest.is_file():
            summary["skipped"].append(packet["asset_id"])
            continue
        left = remaining_calls(load_ledger(), cap=cap)
        if left <= 0:
            summary["failed"].append({"asset_id": packet["asset_id"], "error": "cap reached"})
            break
        try:
            row = generate_png(
                prompt=packet["prompt"],
                dest=dest,
                asset_id=packet["asset_id"],
                role=packet["role"],
                model=packet.get("model") or INTERIOR_MODEL,
                remaining_calls=left,
            )
            if accept_all:
                accepted.write_bytes(dest.read_bytes())
                row["accepted"] = True
                row["status"] = "accepted"
                row["accepted_path"] = str(accepted.relative_to(ROOT))
            append_asset(row)
            summary["generated"].append(packet["asset_id"])
        except PaidImageError as exc:
            append_asset(
                {
                    "asset_id": packet["asset_id"],
                    "role": packet["role"],
                    "status": "rejected",
                    "accepted": False,
                    "paid_call": True,
                    "error": str(exc)[:400],
                    "model": packet.get("model"),
                    "size": packet.get("size") or FALLBACK_SIZE,
                }
            )
            summary["failed"].append({"asset_id": packet["asset_id"], "error": str(exc)[:400]})
            # No hidden retry. Stop the loop only if the cap is exhausted.
    ledger = load_ledger()
    summary["paid_image_calls"] = ledger.get("paid_image_calls", 0)
    summary["estimated_spend_usd"] = ledger.get("estimated_spend_usd", 0)
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
