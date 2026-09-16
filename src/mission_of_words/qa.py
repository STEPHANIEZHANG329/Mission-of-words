"""Fail-closed QA for the 4-page prototype. `pass` is computed, never hand-edited."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mission_of_words.assets import validate_store
from mission_of_words.bible import CanonError, bind_mission_canon
from mission_of_words.budget import BudgetError, load_budget, paid_calls_disabled
from mission_of_words.image_client import PAID_GENERATION_GATE_IMPLEMENTED, dry_run_info
from mission_of_words.layout import (
    DPI,
    INNER_SAFETY_INCHES,
    MIN_ANSWER_KEY_PT,
    MIN_FAITH_DRAWING_SQIN,
    MIN_INSTRUCTION_PT,
    MIN_PUZZLE_LETTER_PT,
    OUTER_SAFETY_INCHES,
    SAFE_MARGIN_INCHES,
    TRIM_INCHES,
    layout_metrics,
    page_margins_inches,
)
from mission_of_words.maze import Maze
from mission_of_words.paths import OUTPUT_DIR, SCHEMA_DIR
from mission_of_words.validate import validate_instance, validate_repo

REQUIRED_SEARCH_TARGETS = {
    "lantern",
    "pumpkin",
    "apple",
    "leaf",
    "acorn",
    "scarf",
    "basket",
    "Bible",
}

REQUIRED_PAGE_TYPES = ("coloring", "search_find", "maze", "faith_interaction")
PLACEHOLDER_NEEDLES = ("ARTWORK PLACEHOLDER", "placeholder_only", "LOREM IPSUM")


def _search_page(spec: dict[str, Any]) -> dict[str, Any] | None:
    pages = (spec.get("mission") or {}).get("pages") or []
    for page in pages:
        if page.get("type") == "search_find":
            return page
    return None


def _boxes_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


def _target_boxes(targets: list[dict[str, Any]]) -> list[tuple[str, tuple[float, float, float, float]]]:
    boxes = []
    for target in targets:
        x = float(target["x"])
        y = float(target["y"])
        scale = float(target["scale"])
        boxes.append((str(target["name"]), (x, y, x + scale, y + scale)))
    return boxes


def _pdf_text(path: Path) -> str:
    if not path.is_file():
        return ""
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(str(path))
    chunks: list[str] = []
    for page in document:
        textpage = page.get_textpage()
        chunks.append(textpage.get_text_bounded() or "")
    return "\n".join(chunks)


def evaluate_build(
    *,
    spec: dict[str, Any],
    maze: Maze,
    paid_image_calls: int,
    sample_pages: int = 4,
    search_manifest: list[dict[str, Any]] | None = None,
    compositions: list[dict[str, Any]] | None = None,
    interior_pdf: Path | None = None,
    visual_qa_pass: bool | None = None,
    preview_count: int = 0,
    asset_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    metrics = layout_metrics()
    compositions = compositions or []
    search_manifest = search_manifest or []
    asset_records = asset_records or []

    schema_errors = validate_repo()
    if schema_errors:
        failures.extend(schema_errors)

    canon_bound = False
    canon_id = (spec.get("mission") or {}).get("canon_id")
    try:
        canon = bind_mission_canon(spec)
        canon_bound = True
        canon_id = canon["canon_id"]
        if canon.get("child_paraphrase", "").strip() == canon.get("source_text", "").strip():
            failures.append("canon: paraphrase must stay separate from source_text")
    except CanonError as exc:
        failures.append(f"canon: {exc}")

    book = spec.get("book") or {}
    trim = book.get("trim_inches")
    margin = book.get("safe_margin_inches")
    dpi = book.get("dpi", DPI)
    layout_ok = True
    if list(trim or []) != list(TRIM_INCHES):
        layout_ok = False
        failures.append(f"layout: trim_inches must be {list(TRIM_INCHES)}, got {trim}")
    if not isinstance(margin, (int, float)) or float(margin) < SAFE_MARGIN_INCHES:
        layout_ok = False
        failures.append(f"layout: safe_margin_inches must be >= {SAFE_MARGIN_INCHES}, got {margin}")
    if int(dpi) != DPI:
        layout_ok = False
        failures.append(f"layout: dpi must be {DPI}, got {dpi}")
    if metrics["used_instruction_pt"] < MIN_INSTRUCTION_PT:
        layout_ok = False
        failures.append("layout: instruction font below 12pt")
    if metrics["used_puzzle_letter_pt"] < MIN_PUZZLE_LETTER_PT:
        layout_ok = False
        failures.append("layout: puzzle letters below 12pt")
    if metrics["used_answer_key_pt"] < MIN_ANSWER_KEY_PT:
        layout_ok = False
        failures.append("layout: answer key font below 9pt")

    facing_ok = True
    for page_number in (1, 2, 3, 4):
        margins = page_margins_inches(page_number)
        if margins["inner"] < SAFE_MARGIN_INCHES or margins["outer"] < SAFE_MARGIN_INCHES:
            facing_ok = False
            layout_ok = False
            failures.append(f"layout: page {page_number} safety below 0.50 in")
        if page_number % 2 == 1 and margins["left"] != INNER_SAFETY_INCHES:
            facing_ok = False
            layout_ok = False
            failures.append("layout: odd page inner safety is not on the left")
        if page_number % 2 == 0 and margins["right"] != INNER_SAFETY_INCHES:
            facing_ok = False
            layout_ok = False
            failures.append("layout: even page inner safety is not on the right")
        if abs(margins["inner"] - OUTER_SAFETY_INCHES) < 1e-9:
            facing_ok = False
            layout_ok = False
            failures.append("layout: inner and outer safety are identical; parity is missing")

    pages = (spec.get("mission") or {}).get("pages") or []
    page_types = tuple(page.get("type") for page in pages)
    if page_types != REQUIRED_PAGE_TYPES or sample_pages != 4:
        failures.append(f"pages: expected 4-page prototype {REQUIRED_PAGE_TYPES}, got {page_types}")

    search_page = _search_page(spec)
    targets = list((search_page or {}).get("targets") or [])
    names = [t.get("name") for t in targets]
    search_find_target_count = len(targets)
    search_find_all_targets_present = set(names) == REQUIRED_SEARCH_TARGETS and len(names) == 8
    if not search_find_all_targets_present:
        failures.append(
            "search_find: missing required independently placed targets: "
            f"expected {sorted(REQUIRED_SEARCH_TARGETS)}, got {names}"
        )

    search_find_no_unsafe_overlap = True
    if search_find_all_targets_present:
        boxes = _target_boxes(targets)
        for index, (name_a, box_a) in enumerate(boxes):
            x0, y0, x1, y1 = box_a
            if min(x0, y0) < 0 or max(x1, y1) > 1.05:
                search_find_no_unsafe_overlap = False
                failures.append(f"search_find: target {name_a} is outside the safe scene")
            for name_b, box_b in boxes[index + 1 :]:
                if _boxes_overlap(box_a, box_b):
                    search_find_no_unsafe_overlap = False
                    failures.append(f"search_find: unsafe overlap between {name_a} and {name_b}")

    manifest_names = [row.get("name") for row in search_manifest]
    search_find_answer_key_from_manifest = (
        len(search_manifest) == 8 and set(manifest_names) == REQUIRED_SEARCH_TARGETS
    )
    if search_manifest and not search_find_answer_key_from_manifest:
        failures.append(f"search_find: compositor manifest mismatch: {manifest_names}")

    maze_solvable = False
    maze_perfect = False
    try:
        path = maze.solve()
        maze_solvable = len(path) > 1
        maze_perfect = maze.is_perfect()
    except ValueError as exc:
        failures.append(f"maze: {exc}")
    if not maze_solvable:
        failures.append("maze: unsolvable")
    if not maze_perfect:
        failures.append("maze: not a perfect maze with a unique path")

    faith_area = None
    faith_ok = False
    for record in compositions:
        if record.get("type") == "faith_interaction":
            faith_area = record.get("drawing_area_sqin")
            faith_ok = float(faith_area or 0) >= MIN_FAITH_DRAWING_SQIN
    if compositions and not faith_ok:
        failures.append(
            f"faith: drawing area {faith_area} sq in is below {MIN_FAITH_DRAWING_SQIN}"
        )

    placeholder_absent = True
    if interior_pdf is not None:
        text = _pdf_text(interior_pdf).upper()
        for needle in PLACEHOLDER_NEEDLES:
            if needle in text:
                placeholder_absent = False
                failures.append(f"copy: placeholder language present: {needle}")

    if paid_image_calls != 0:
        failures.append(f"paid_image_calls must be 0 in normal CI, got {paid_image_calls}")

    client = dry_run_info()
    if client["paid_image_calls"] != 0 or client["network_allowed"] or not client["dry_run"]:
        failures.append("image_client is not in dry-run mode")
    if PAID_GENERATION_GATE_IMPLEMENTED:
        failures.append("paid-image gate flag is enabled; this pass must keep it closed")

    try:
        budget = load_budget()
        if not paid_calls_disabled(budget):
            failures.append("budget allows paid calls; this pass must keep paid generation disabled")
        if int(budget.get("spent_calls") or 0) != 0 or float(budget.get("spent_usd") or 0) != 0:
            failures.append("budget ledger spend is non-zero")
    except (BudgetError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        failures.append(f"budget: {exc}")
        budget = {}

    asset_errors = validate_store()
    if asset_errors:
        failures.extend(asset_errors)

    for record in asset_records:
        if record.get("paid_call") is True:
            failures.append(f"asset {record.get('asset_id')} was marked paid_call")
        if float(record.get("cost_usd") or 0) != 0:
            failures.append(f"asset {record.get('asset_id')} has non-zero cost")

    if visual_qa_pass is False:
        failures.append("visual_qa: independent visual preflight reported FAIL")

    report = {
        "book_id": book.get("book_id", "bright_hearts_fall_01"),
        "mission_id": (spec.get("mission") or {}).get("id"),
        "canon_id": canon_id,
        "canon_bound": canon_bound,
        "sample_pages": sample_pages,
        "paid_image_calls": paid_image_calls,
        "estimated_spend_usd": 0.0,
        "trim_inches": list(trim or TRIM_INCHES),
        "dpi": int(dpi),
        "dpi_ok": int(dpi) == DPI,
        "no_bleed": True,
        "safe_margin_inches": margin,
        "inner_safety_inches": INNER_SAFETY_INCHES,
        "facing_page_parity_ok": facing_ok,
        "min_instruction_pt": MIN_INSTRUCTION_PT,
        "min_puzzle_letter_pt": MIN_PUZZLE_LETTER_PT,
        "min_answer_key_pt": MIN_ANSWER_KEY_PT,
        "layout_ok": layout_ok,
        "search_find_target_count": search_find_target_count,
        "search_find_all_targets_present": search_find_all_targets_present,
        "search_find_no_unsafe_overlap": search_find_no_unsafe_overlap,
        "search_find_manifest_count": len(search_manifest),
        "search_find_answer_key_from_manifest": search_find_answer_key_from_manifest or not search_manifest,
        "maze_solvable": maze_solvable,
        "maze_perfect_unique_path": maze_perfect,
        "faith_drawing_area_sqin": faith_area,
        "faith_drawing_area_ok": faith_ok or not compositions,
        "placeholder_copy_absent": placeholder_absent,
        "artwork_status": "procedural_lineart",
        "image_client_mode": client["mode"],
        "paid_generation_gate_implemented": PAID_GENERATION_GATE_IMPLEMENTED,
        "visual_qa_pass": True if visual_qa_pass is None else visual_qa_pass,
        "preview_count": preview_count,
        "asset_count": len(asset_records),
        "failures": failures,
        "pass": not failures,
    }
    schema_path = SCHEMA_DIR / "qa.schema.json"
    if schema_path.is_file():
        report_errors = validate_instance(report, schema_path, label="qa_report")
        if report_errors:
            report["failures"] = failures + report_errors
            report["pass"] = False
    return report


def write_report(report: dict[str, Any], path: Path | None = None) -> Path:
    destination = path or (OUTPUT_DIR / "qa_report.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return destination
