"""Fail-closed production QA. Separate from the Phase B technical-proof evaluator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mission_of_words.full_book_qa import (
    TARGET_PAGE_COUNT,
    _pdf_page_count,
    answer_key_linkage_failures,
    evaluate_full_book,
)
from mission_of_words.layout import (
    DPI,
    USED_ANSWER_KEY_PT,
    USED_INSTRUCTION_PT,
    USED_PUZZLE_LETTER_PT,
)
from mission_of_words.maze import Maze
from mission_of_words.paid_images import MAX_PAID_CALLS


def evaluate_production(
    *,
    manifest: dict[str, Any],
    missions: list[dict[str, Any]],
    compositions: list[dict[str, Any]],
    visual: dict[str, Any],
    interior_pdf: Path,
    answer_pdf: Path | None,
    mazes: dict[str, Maze],
    search_manifests: dict[str, list[dict[str, Any]]],
    ledger: dict[str, Any],
    preview_count: int,
    asset_records: list[dict[str, Any]],
) -> dict[str, Any]:
    base = evaluate_full_book(
        manifest=manifest,
        missions=missions,
        paid_image_calls=0,
        interior_pdf=None,
        compositions=None,
        mazes=mazes,
        search_manifests=search_manifests,
        visual_readiness=visual.get("visual_readiness"),
        preview_count=preview_count,
        asset_records=[],
        answer_pdf=None,
    )

    failures = [
        item
        for item in base["failures"]
        if "paid_image_calls" not in item
        and "placeholder" not in item.lower()
        and "accepted production artwork" not in item
        and "image_client is not in dry-run" not in item
        and "paid-image gate" not in item
        and "budget allows paid" not in item
        and "authorizes paid" not in item
        and "Phase B assets must stay placeholders" not in item
    ]

    paid = int(ledger.get("paid_image_calls") or 0)
    if paid > MAX_PAID_CALLS:
        failures.append(f"paid_image_calls {paid} exceeds Owner cap {MAX_PAID_CALLS}")

    rendered = _pdf_page_count(interior_pdf) if interior_pdf.is_file() else 0
    if rendered != TARGET_PAGE_COUNT:
        failures.append(
            f"production interior must have {TARGET_PAGE_COUNT} pages, got {rendered}"
        )
    if answer_pdf and answer_pdf.is_file() and _pdf_page_count(answer_pdf) != 8:
        failures.append("production answer-key PDF must have 8 pages")

    placeholder_pages = [
        int(record["page"])
        for record in compositions
        if record.get("placeholder")
        or record.get("artwork_status") in {"unfilled_slot", "placeholder_only"}
    ]
    if placeholder_pages:
        failures.append(f"placeholder art remains on pages {placeholder_pages}")

    layout_bad = [
        int(record["page"])
        for record in compositions
        if record.get("collisions") or record.get("overflow") or record.get("clipped")
    ]
    if layout_bad:
        failures.append(
            f"layout collisions/overflow/clipping on pages {layout_bad}"
        )

    if (
        USED_INSTRUCTION_PT < 12
        or USED_PUZZLE_LETTER_PT < 12
        or USED_ANSWER_KEY_PT < 9
    ):
        failures.append("font floors broken")

    for record in compositions:
        if record.get("type") == "search_find":
            names = [row.get("name") for row in record.get("manifest") or []]
            if len(names) != 8:
                failures.append(
                    f"search page {record.get('page')} does not have 8 targets"
                )
            dpi = float(record.get("effective_dpi") or 0)
            if dpi + 0.05 < DPI:
                failures.append(
                    f"search page {record.get('page')} effective DPI {dpi:.1f} is below {DPI}"
                )

    human_missing = [
        page["page"]
        for page in visual.get("pages") or []
        if not (page.get("human_visual_review") or {}).get("pass")
    ]
    if human_missing:
        failures.append(
            f"Human/PM Visual Review missing or FAIL on pages {human_missing}"
        )

    if visual.get("visual_readiness") != "PASS" or visual.get("pass") is not True:
        failures.append("independent visual QA is not PASS")

    failures.extend(
        answer_key_linkage_failures(
            manifest_pages=list(manifest.get("pages") or []),
            missions=missions,
        )
    )

    technical_ok = (
        rendered == TARGET_PAGE_COUNT
        and not layout_bad
        and not placeholder_pages
        and bool(base.get("maze_all_solvable"))
        and bool(base.get("maze_all_unique"))
        and bool(base.get("search_answer_keys_from_manifest"))
        and bool(base.get("facing_page_parity_ok"))
        and bool(base.get("font_floors_ok"))
        and bool(base.get("answer_key_linkage_ok"))
        and bool(base.get("all_canons_bound"))
    )

    production_pass = (
        technical_ok
        and not failures
        and visual.get("pass") is True
        and not placeholder_pages
    )

    report = dict(base)
    report.update(
        {
            "phase": "C",
            "paid_image_calls": paid,
            "estimated_spend_usd": float(ledger.get("estimated_spend_usd") or 0),
            "rendered_page_count": rendered,
            "interior_pdf_present": interior_pdf.is_file(),
            "placeholder_assets_present": bool(placeholder_pages),
            "unfilled_art_slots": len(placeholder_pages),
            "visual_readiness": visual.get("visual_readiness"),
            "non_production_mark_present": False,
            "technical_pass": bool(technical_ok),
            "production_pass": bool(production_pass),
            "pass": bool(production_pass),
            "failures": failures,
            "blockers": [] if production_pass else failures,
            "image_client_mode": "gpt2-openai" if paid else "dry-run",
            "paid_generation_gate_implemented": True,
            "artwork_status_summary": "accepted" if not placeholder_pages else "mixed",
        }
    )
    return report
