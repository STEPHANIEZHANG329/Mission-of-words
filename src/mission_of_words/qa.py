"""Fail-closed QA. Technical success is not prototype/production success."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mission_of_words.assets import (
    REQUIRED_SEARCH_TARGET_NAMES,
    accepted_artwork_inventory,
    validate_store,
)
from mission_of_words.bible import CanonError, bind_mission_canon
from mission_of_words.budget import BudgetError, load_budget, paid_calls_disabled
from mission_of_words.image_client import PAID_GENERATION_GATE_IMPLEMENTED, dry_run_info
from mission_of_words.layout import (
    DPI,
    MIN_ANSWER_KEY_PT,
    MIN_INSTRUCTION_PT,
    MIN_PUZZLE_LETTER_PT,
    SAFE_MARGIN_INCHES,
    TRIM_INCHES,
    facing_page_report,
    layout_metrics,
    search_find_print_space,
)
from mission_of_words.maze import Maze
from mission_of_words.paths import OUTPUT_DIR, SCHEMA_DIR, VISUAL_QA_PATH
from mission_of_words.validate import validate_file, validate_instance, validate_repo

REQUIRED_SEARCH_TARGETS = REQUIRED_SEARCH_TARGET_NAMES
REQUIRED_PAGE_TYPES = ("coloring", "search_find", "maze", "faith_interaction")
VISUAL_GATES = ("asset_integration", "child_usability", "prompt_to_art")
PAGE_VISUAL_KEYS = ("1", "2", "3", "4")


def _search_page(spec: dict[str, Any]) -> dict[str, Any] | None:
    pages = (spec.get("mission") or {}).get("pages") or []
    for page in pages:
        if page.get("type") == "search_find":
            return page
    return None


def _gate_record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _gate_passed(record: Any, *, label: str, prototype_failures: list[str]) -> str:
    """Missing evidence or non-pass is a prototype/production failure."""
    data = _gate_record(record)
    status = data.get("status")
    evidence = data.get("evidence_ref") or data.get("evidence")
    if status is None:
        prototype_failures.append(f"visual_qa: {label} evidence is missing")
        return "missing"
    if status != "pass":
        prototype_failures.append(f"visual_qa: {label} is {status}")
        return str(status)
    if not evidence:
        prototype_failures.append(f"visual_qa: {label} PASS is missing evidence_ref")
        return "missing"
    return "pass"


def load_visual_qa(path: Path | None = None) -> dict[str, Any]:
    visual_path = path or VISUAL_QA_PATH
    if visual_path is None or not visual_path.is_file():
        return {}
    try:
        payload = json.loads(visual_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def evaluate_visual_qa(evidence: dict[str, Any] | None) -> tuple[dict[str, Any], list[str], list[str]]:
    prototype_failures: list[str] = []
    payload = evidence if isinstance(evidence, dict) else {}
    if not payload:
        prototype_failures.append("visual_qa: independent visual QA evidence is missing")
    gates = {name: _gate_passed(payload.get(name), label=name, prototype_failures=prototype_failures) for name in VISUAL_GATES}
    pages = {}
    page_block = payload.get("pages") if isinstance(payload.get("pages"), dict) else {}
    for key in PAGE_VISUAL_KEYS:
        pages[key] = _gate_passed(
            page_block.get(key) or page_block.get(int(key)),
            label=f"page {key} visual QA",
            prototype_failures=prototype_failures,
        )
    owner = _gate_passed(
        payload.get("owner_production_signoff"),
        label="owner_production_signoff",
        prototype_failures=prototype_failures,
    )
    # Owner sign-off is production-only; keep it out of prototype_failures list by moving later.
    owner_failures = [item for item in prototype_failures if "owner_production_signoff" in item]
    prototype_failures = [item for item in prototype_failures if "owner_production_signoff" not in item]
    summary = {
        "asset_integration": gates["asset_integration"],
        "child_usability": gates["child_usability"],
        "prompt_to_art": gates["prompt_to_art"],
        "pages": pages,
        "owner_production_signoff": owner,
        "all_required_gates_passed": not prototype_failures,
        "missing_evidence": any(value != "pass" for value in list(gates.values()) + list(pages.values())),
        "owner_failures": owner_failures,
    }
    return summary, prototype_failures, owner_failures


def evaluate_build(
    *,
    spec: dict[str, Any],
    maze: Maze,
    paid_image_calls: int,
    sample_pages: int = 4,
    visual_qa: dict[str, Any] | None = None,
    assets_root: Path | None = None,
    visual_qa_path: Path | None = None,
) -> dict[str, Any]:
    technical_failures: list[str] = []
    prototype_failures: list[str] = []
    production_failures: list[str] = []
    metrics = layout_metrics()

    schema_errors = validate_repo()
    if schema_errors:
        technical_failures.extend(schema_errors)

    canon_bound = False
    canon_id = (spec.get("mission") or {}).get("canon_id")
    try:
        canon = bind_mission_canon(spec)
        canon_bound = True
        canon_id = canon["canon_id"]
    except CanonError as exc:
        technical_failures.append(f"canon: {exc}")

    book = spec.get("book") or {}
    trim = book.get("trim_inches")
    margin = book.get("safe_margin_inches")
    inner = book.get("inner_margin_inches", margin)
    outer = book.get("outer_margin_inches", margin)
    dpi = book.get("dpi", DPI)
    layout_ok = True
    if list(trim or []) != list(TRIM_INCHES):
        layout_ok = False
        technical_failures.append(f"layout: trim_inches must be {list(TRIM_INCHES)}, got {trim}")
    if not isinstance(margin, (int, float)) or float(margin) < SAFE_MARGIN_INCHES:
        layout_ok = False
        technical_failures.append(f"layout: safe_margin_inches must be >= {SAFE_MARGIN_INCHES}, got {margin}")
    if int(dpi) != DPI:
        layout_ok = False
        technical_failures.append(f"layout: dpi must be {DPI}, got {dpi}")
    if metrics["used_instruction_pt"] < MIN_INSTRUCTION_PT:
        layout_ok = False
        technical_failures.append("layout: instruction font below 12pt")
    if metrics["used_puzzle_letter_pt"] < MIN_PUZZLE_LETTER_PT:
        layout_ok = False
        technical_failures.append("layout: puzzle letters below 12pt")
    if metrics["used_answer_key_pt"] < MIN_ANSWER_KEY_PT:
        layout_ok = False
        technical_failures.append("layout: answer key font below 9pt")

    facing = facing_page_report(
        inner_inches=float(inner) if isinstance(inner, (int, float)) else None,
        outer_inches=float(outer) if isinstance(outer, (int, float)) else None,
        page_count=4,
    )
    facing_ok = bool(facing["ok"])
    if not facing_ok:
        layout_ok = False
        technical_failures.append("layout: facing-page inner/outer safety is below 0.50 inch")
    for page in facing["pages"]:
        if float(page["inner_inches"]) < SAFE_MARGIN_INCHES or float(page["outer_inches"]) < SAFE_MARGIN_INCHES:
            layout_ok = False
            technical_failures.append(
                f"layout: page {page['page']} ({page['side']}) inner={page['inner_inches']} outer={page['outer_inches']}"
            )

    pages = (spec.get("mission") or {}).get("pages") or []
    page_types = tuple(page.get("type") for page in pages)
    if page_types != REQUIRED_PAGE_TYPES or sample_pages != 4:
        technical_failures.append(f"pages: expected 4-page prototype {REQUIRED_PAGE_TYPES}, got {page_types}")

    search_page = _search_page(spec)
    targets = list((search_page or {}).get("targets") or [])
    names = [t.get("name") for t in targets]
    search_find_target_count = len(targets)
    search_find_all_targets_present = set(names) == REQUIRED_SEARCH_TARGETS and len(names) == 8
    if not search_find_all_targets_present:
        technical_failures.append(
            "search_find: missing required independently placed targets: "
            f"expected {sorted(REQUIRED_SEARCH_TARGETS)}, got {names}"
        )

    print_space = {
        "ok": False,
        "targets": [],
        "all_inside_safe_rect": False,
        "no_unsafe_overlap": False,
        "defects": ["search_find: no print-space placements"],
    }
    if search_find_all_targets_present:
        print_space = search_find_print_space(
            targets,
            inner_inches=float(inner) if isinstance(inner, (int, float)) else None,
            outer_inches=float(outer) if isinstance(outer, (int, float)) else None,
        )
        if not print_space["ok"]:
            technical_failures.extend(print_space["defects"])

    maze_solvable = False
    maze_perfect = False
    try:
        path = maze.solve()
        maze_solvable = len(path) > 1
        maze_perfect = maze.is_perfect()
    except ValueError as exc:
        technical_failures.append(f"maze: {exc}")
    if not maze_solvable:
        technical_failures.append("maze: unsolvable")
    if not maze_perfect:
        technical_failures.append("maze: not a perfect maze with a unique path")

    if paid_image_calls != 0:
        technical_failures.append(f"paid_image_calls must be 0 in normal CI, got {paid_image_calls}")

    client = dry_run_info()
    if client["paid_image_calls"] != 0 or client["network_allowed"] or not client["dry_run"]:
        technical_failures.append("image_client is not in dry-run mode")
    if PAID_GENERATION_GATE_IMPLEMENTED:
        technical_failures.append("paid-image gate flag is enabled; V1 must keep it closed")

    try:
        budget = load_budget()
        if not paid_calls_disabled(budget):
            technical_failures.append("budget allows paid calls; V1 must keep paid generation disabled")
        if int(budget.get("spent_calls") or 0) != 0 or float(budget.get("spent_usd") or 0) != 0:
            technical_failures.append("budget ledger spend is non-zero")
    except (BudgetError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        technical_failures.append(f"budget: {exc}")

    asset_errors = validate_store(assets_root)
    if asset_errors:
        technical_failures.extend(asset_errors)

    inventory = accepted_artwork_inventory(assets_root)
    accepted_artwork_complete = bool(inventory["complete"])
    artwork_status = "accepted" if accepted_artwork_complete else "placeholder_only"
    coloring = next((page for page in pages if page.get("type") == "coloring"), {})
    if coloring.get("artwork_status") == "placeholder_only":
        artwork_status = "placeholder_only"
    if artwork_status == "placeholder_only":
        prototype_failures.append("artwork_status is placeholder_only; prototype/production cannot pass")
    if not accepted_artwork_complete:
        prototype_failures.extend(f"accepted_art: missing {item}" for item in inventory["missing"])

    evidence = visual_qa if visual_qa is not None else load_visual_qa(visual_qa_path)
    visual_summary, visual_failures, owner_failures = evaluate_visual_qa(evidence)
    prototype_failures.extend(visual_failures)
    production_failures.extend(owner_failures)
    if visual_qa_path is None and visual_qa is None:
        schema_visual = SCHEMA_DIR / "visual_qa.schema.json"
        if VISUAL_QA_PATH.is_file() and schema_visual.is_file():
            visual_schema_errors = validate_file(VISUAL_QA_PATH, schema_visual, label="visual_qa")
            technical_failures.extend(visual_schema_errors)

    technical_pass = not technical_failures
    prototype_pass = technical_pass and not prototype_failures
    if not prototype_pass:
        production_failures.append("production_pass requires prototype_pass")
    production_pass = prototype_pass and not production_failures
    # `pass` is production/publish readiness only. Technical PDF success must not set it.
    overall_pass = production_pass
    failures = technical_failures + prototype_failures + production_failures

    report = {
        "book_id": book.get("book_id", "bright_hearts_fall_01"),
        "mission_id": (spec.get("mission") or {}).get("id"),
        "canon_id": canon_id,
        "canon_bound": canon_bound,
        "sample_pages": sample_pages,
        "paid_image_calls": paid_image_calls,
        "trim_inches": list(trim or TRIM_INCHES),
        "dpi": int(dpi),
        "dpi_ok": int(dpi) == DPI,
        "safe_margin_inches": margin,
        "inner_margin_inches": inner,
        "outer_margin_inches": outer,
        "min_instruction_pt": MIN_INSTRUCTION_PT,
        "min_puzzle_letter_pt": MIN_PUZZLE_LETTER_PT,
        "min_answer_key_pt": MIN_ANSWER_KEY_PT,
        "layout_ok": layout_ok,
        "facing_page_safety": {
            "ok": facing_ok,
            "pages": [
                {
                    "page": page["page"],
                    "side": page["side"],
                    "inner_edge": page["inner_edge"],
                    "inner_inches": page["inner_inches"],
                    "outer_inches": page["outer_inches"],
                    "ok": page["ok"],
                }
                for page in facing["pages"]
            ],
        },
        "search_find_target_count": search_find_target_count,
        "search_find_all_targets_present": search_find_all_targets_present,
        "search_find_no_unsafe_overlap": bool(print_space.get("no_unsafe_overlap")),
        "search_find_print_space": {
            "ok": bool(print_space.get("ok")),
            "all_inside_safe_rect": bool(print_space.get("all_inside_safe_rect")),
            "no_unsafe_overlap": bool(print_space.get("no_unsafe_overlap")),
            "composed_px": print_space.get("composed_px"),
            "target_count": len(print_space.get("targets") or []),
        },
        "maze_solvable": maze_solvable,
        "maze_perfect_unique_path": maze_perfect,
        "artwork_status": artwork_status,
        "accepted_artwork_complete": accepted_artwork_complete,
        "visual_qa": {
            "asset_integration": visual_summary["asset_integration"],
            "child_usability": visual_summary["child_usability"],
            "prompt_to_art": visual_summary["prompt_to_art"],
            "pages": visual_summary["pages"],
            "owner_production_signoff": visual_summary["owner_production_signoff"],
            "all_required_gates_passed": visual_summary["all_required_gates_passed"],
            "missing_evidence": visual_summary["missing_evidence"],
        },
        "image_client_mode": client["mode"],
        "paid_generation_gate_implemented": PAID_GENERATION_GATE_IMPLEMENTED,
        "technical_failures": technical_failures,
        "prototype_failures": prototype_failures,
        "production_failures": production_failures,
        "failures": failures,
        "technical_pass": technical_pass,
        "prototype_pass": prototype_pass,
        "production_pass": production_pass,
        "pass": overall_pass,
    }
    schema_path = SCHEMA_DIR / "qa.schema.json"
    if schema_path.is_file():
        report_errors = validate_instance(report, schema_path, label="qa_report")
        if report_errors:
            technical_failures.extend(report_errors)
            report["technical_failures"] = technical_failures
            report["failures"] = technical_failures + prototype_failures + production_failures
            report["technical_pass"] = False
            report["prototype_pass"] = False
            report["production_pass"] = False
            report["pass"] = False
    return report


def write_report(report: dict[str, Any], path: Path | None = None) -> Path:
    destination = path or (OUTPUT_DIR / "qa_report.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return destination
