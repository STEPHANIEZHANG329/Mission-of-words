"""Fail-closed QA for the 48-page Bright Hearts book.

`pass` is production readiness only and is computed, never hand-edited.
Phase A can earn `blueprint_pass`. It cannot earn `technical_pass` or
`production_pass`: there is no 48-page composed proof yet, and every art
slot is unfilled.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mission_of_words.bible import CanonError, bind_mission_record, load_all_canons
from mission_of_words.book_manifest import (
    TARGET_PAGE_COUNT,
    build_manifest,
    load_manifest,
    load_mission_records,
    manifest_consistency_errors,
    page_map,
)
from mission_of_words.budget import BudgetError, load_budget, paid_calls_disabled
from mission_of_words.image_client import PAID_GENERATION_GATE_IMPLEMENTED, dry_run_info, paid_call_count
from mission_of_words.layout import (
    DPI,
    INNER_SAFETY_INCHES,
    MIN_ANSWER_KEY_PT,
    MIN_INSTRUCTION_PT,
    MIN_PUZZLE_LETTER_PT,
    OUTER_SAFETY_INCHES,
    SAFE_MARGIN_INCHES,
    TRIM_INCHES,
    USED_ANSWER_KEY_PT,
    USED_INSTRUCTION_PT,
    USED_PUZZLE_LETTER_PT,
    page_margins_inches,
)
from mission_of_words.paths import BOOK_RECORD, OUTPUT_DIR, SCHEMA_DIR
from mission_of_words.validate import validate_instance, validate_repo

PHASE_B_BLOCKERS = [
    "Phase B: generalize build_sample into a 48-page deterministic build",
    "Phase B: front-matter and back-matter templates are not rendered yet",
    "Phase B: maze/search-find generators are not yet run for missions 2-8",
    "Phase B: no 48-page technical proof PDF exists",
    "Phase B: contact sheets of all 48 pages are not generated",
    "Phase C: paid artwork is not authorized; prompt packets exist only as visual_prompt fields",
    "Phase D: production_pass cannot become true while art slots are unfilled",
    "Phase E: cover is deferred until interior page count is locked and Owner-approved",
    "Do not merge, publish, or upload to KDP without Owner approval",
]


def _boxes_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


def uniqueness_failures(missions: list[dict[str, Any]], pages: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    mechanics = [str(page.get("activity_mechanic") or "") for page in pages]
    if len(mechanics) != len(set(mechanics)):
        dupes = sorted({item for item in mechanics if mechanics.count(item) > 1})
        failures.append(f"uniqueness: duplicated activity_mechanic values: {dupes}")

    titles = [str(page.get("title") or "") for page in pages]
    if len(titles) != len(set(titles)):
        dupes = sorted({item for item in titles if titles.count(item) > 1})
        failures.append(f"uniqueness: duplicated page titles: {dupes}")

    search_sets: list[tuple[str, frozenset[str]]] = []
    maze_seeds: list[tuple[str, int]] = []
    coloring_objects: list[tuple[str, frozenset[str]]] = []
    faith_choices: list[tuple[str, tuple[str, ...]]] = []
    instructions: list[tuple[str, str]] = []

    for mission in missions:
        mission_id = str(mission["id"])
        for page in mission["pages"]:
            page_type = page["type"]
            instruction = str(page.get("child_instruction") or page.get("instruction") or "").strip()
            if instruction:
                instructions.append((f"{mission_id}:{page_type}", instruction))
            if page_type == "search_find":
                names = [str(target["name"]) for target in page.get("targets") or []]
                search_sets.append((mission_id, frozenset(names)))
            elif page_type == "maze":
                maze_seeds.append((mission_id, int(page["seed"])))
            elif page_type == "coloring":
                coloring_objects.append((mission_id, frozenset(page.get("required_objects") or [])))
            elif page_type == "faith_interaction":
                labels = tuple(choice["label"] for choice in page.get("choices") or [])
                faith_choices.append((mission_id, labels))

    def _dupes(pairs: list[tuple[str, Any]], label: str) -> None:
        seen: dict[Any, str] = {}
        for owner, value in pairs:
            if value in seen:
                failures.append(
                    f"uniqueness: {label} copied from {seen[value]} onto {owner}"
                )
            else:
                seen[value] = owner

    _dupes(search_sets, "search-find target set")
    _dupes(maze_seeds, "maze seed")
    _dupes(coloring_objects, "coloring required_objects")
    _dupes(faith_choices, "faith choice labels")
    _dupes(instructions, "child instruction")

    canon_ids = [mission["canon_id"] for mission in missions]
    if len(canon_ids) != len(set(canon_ids)):
        failures.append("uniqueness: two missions share the same canon_id")
    titles_m = [mission["title"] for mission in missions]
    if len(titles_m) != len(set(titles_m)):
        failures.append("uniqueness: two missions share the same title")
    return failures


def answer_key_linkage_failures(
    *,
    manifest_pages: list[dict[str, Any]],
    missions: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    by_number = {int(page["page"]): page for page in manifest_pages}
    activity_needing_keys: dict[int, str] = {}
    for page in manifest_pages:
        if page.get("type") in {"search_find", "maze"}:
            activity_needing_keys[int(page["page"])] = str(page["type"])
            key_page = page.get("answer_key_page")
            if not isinstance(key_page, int):
                failures.append(
                    f"answer_key: {page['type']} page {page['page']} has no answer_key_page"
                )
                continue
            key = by_number.get(key_page)
            if not key or key.get("type") != "answer_key":
                failures.append(
                    f"answer_key: page {page['page']} points at {key_page}, which is not an answer key"
                )
            elif int(page["page"]) not in set(key.get("answers_activity_pages") or []):
                failures.append(
                    f"answer_key: page {key_page} does not list activity page {page['page']}"
                )

    answered: set[int] = set()
    for page in manifest_pages:
        if page.get("type") != "answer_key":
            continue
        sources = list(page.get("answer_sources") or [])
        listed = list(page.get("answers_activity_pages") or [])
        if len(sources) != 2 or len(listed) != 2:
            failures.append(
                f"answer_key: page {page['page']} must map exactly two activities (search_find + maze)"
            )
            continue
        source_pages = [int(item["activity_page"]) for item in sources]
        if sorted(source_pages) != sorted(int(item) for item in listed):
            failures.append(
                f"answer_key: page {page['page']} answers_activity_pages do not match answer_sources"
            )
        for item in sources:
            activity_page = int(item["activity_page"])
            answered.add(activity_page)
            activity = by_number.get(activity_page)
            if not activity:
                failures.append(
                    f"answer_key: page {page['page']} points at missing activity {activity_page}"
                )
                continue
            if activity.get("type") != item.get("mechanic"):
                failures.append(
                    f"answer_key: page {page['page']} mechanic {item.get('mechanic')} "
                    f"does not match activity type {activity.get('type')}"
                )
            expected_source = (
                "compositor_manifest" if item.get("mechanic") == "search_find" else "unique_maze_path"
            )
            if item.get("source") != expected_source:
                failures.append(
                    f"answer_key: page {page['page']} source for {item.get('mechanic')} "
                    f"must be {expected_source}"
                )
            if activity.get("mission_id") != page.get("mission_id"):
                failures.append(
                    f"answer_key: page {page['page']} mission_id does not match activity {activity_page}"
                )
    missing = sorted(set(activity_needing_keys) - answered)
    extra = sorted(answered - set(activity_needing_keys))
    if missing:
        failures.append(f"answer_key: activities missing a key page: {missing}")
    if extra:
        failures.append(f"answer_key: key pages point at non-keyed activities: {extra}")

    if len([page for page in manifest_pages if page.get("type") == "answer_key"]) != 8:
        failures.append("answer_key: expected exactly 8 answer-key pages, one per mission")
    if len(missions) != 8:
        failures.append(f"answer_key: expected 8 missions, got {len(missions)}")
    return failures


def search_target_failures(missions: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for mission in missions:
        for page in mission["pages"]:
            if page.get("type") != "search_find":
                continue
            targets = list(page.get("targets") or [])
            names = [target.get("name") for target in targets]
            if len(targets) != 8 or len(set(names)) != 8:
                failures.append(
                    f"search_find: {mission['id']} must have 8 uniquely named targets, got {names}"
                )
                continue
            boxes = []
            for target in targets:
                x = float(target["x"])
                y = float(target["y"])
                scale = float(target["scale"])
                box = (x, y, x + scale, y + scale)
                boxes.append((str(target["name"]), box))
                if min(x, y) < 0 or max(x + scale, y + scale) > 1.05:
                    failures.append(
                        f"search_find: {mission['id']} target {target['name']} is outside the safe scene"
                    )
            for index, (name_a, box_a) in enumerate(boxes):
                for name_b, box_b in boxes[index + 1 :]:
                    if _boxes_overlap(box_a, box_b):
                        failures.append(
                            f"search_find: {mission['id']} unsafe overlap between {name_a} and {name_b}"
                        )
    return failures


def evaluate_full_book(
    *,
    manifest: dict[str, Any] | None = None,
    missions: list[dict[str, Any]] | None = None,
    paid_image_calls: int | None = None,
    interior_pdf: Path | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    missions = missions if missions is not None else load_mission_records()
    try:
        rebuilt = build_manifest(missions=missions)
        manifest = manifest or load_manifest()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        failures.append(f"manifest: {exc}")
        rebuilt = {"pages": []}
        manifest = manifest or {"pages": [], "phase": "A", "book_id": "bright_hearts_fall_01"}

    schema_errors = validate_repo()
    if schema_errors:
        failures.extend(schema_errors)
    failures.extend(manifest_consistency_errors(committed=manifest, rebuilt=rebuilt))

    pages = list(manifest.get("pages") or [])
    numbers = [int(page.get("page") or 0) for page in pages]
    page_count = len(pages)
    if page_count != TARGET_PAGE_COUNT or numbers != list(range(1, TARGET_PAGE_COUNT + 1)):
        failures.append(
            f"pages: expected contiguous pages 1-{TARGET_PAGE_COUNT}, got {numbers[:12]}... ({page_count} pages)"
        )

    facing_ok = True
    for page in pages:
        number = int(page.get("page") or 0)
        if number < 1:
            continue
        margins = page_margins_inches(number)
        if margins["inner"] < SAFE_MARGIN_INCHES or margins["outer"] < SAFE_MARGIN_INCHES:
            facing_ok = False
            failures.append(f"layout: page {number} safety below 0.50 in")
        if number % 2 == 1 and (
            page.get("parity") != "odd"
            or page.get("facing") != "recto"
            or margins["left"] != INNER_SAFETY_INCHES
        ):
            facing_ok = False
            failures.append(f"layout: odd page {number} inner safety is not on the left")
        if number % 2 == 0 and (
            page.get("parity") != "even"
            or page.get("facing") != "verso"
            or margins["right"] != INNER_SAFETY_INCHES
        ):
            facing_ok = False
            failures.append(f"layout: even page {number} inner safety is not on the right")
        if abs(INNER_SAFETY_INCHES - OUTER_SAFETY_INCHES) < 1e-9:
            facing_ok = False
            failures.append("layout: inner and outer safety are identical; parity is missing")

    font_ok = True
    used = {
        "instruction": USED_INSTRUCTION_PT,
        "puzzle": USED_PUZZLE_LETTER_PT,
        "answer_key": USED_ANSWER_KEY_PT,
    }
    floors = {
        "instruction": max(MIN_INSTRUCTION_PT, float(manifest.get("min_instruction_pt") or 0)),
        "puzzle": max(MIN_PUZZLE_LETTER_PT, float(manifest.get("min_puzzle_letter_pt") or 0)),
        "answer_key": max(MIN_ANSWER_KEY_PT, float(manifest.get("min_answer_key_pt") or 0)),
    }
    if used["instruction"] < floors["instruction"]:
        font_ok = False
        failures.append("font: child instruction below 12 pt")
    if used["puzzle"] < floors["puzzle"]:
        font_ok = False
        failures.append("font: puzzle letters below 12 pt")
    if used["answer_key"] < floors["answer_key"]:
        font_ok = False
        failures.append("font: answer key below 9 pt")
    if float(manifest.get("min_instruction_pt") or 0) < MIN_INSTRUCTION_PT:
        font_ok = False
        failures.append("font: manifest min_instruction_pt is below 12")
    if float(manifest.get("min_puzzle_letter_pt") or 0) < MIN_PUZZLE_LETTER_PT:
        font_ok = False
        failures.append("font: manifest min_puzzle_letter_pt is below 12")
    if float(manifest.get("min_answer_key_pt") or 0) < MIN_ANSWER_KEY_PT:
        font_ok = False
        failures.append("font: manifest min_answer_key_pt is below 9")

    trim = list(manifest.get("trim_inches") or [])
    if trim != list(TRIM_INCHES):
        failures.append(f"layout: trim_inches must be {list(TRIM_INCHES)}, got {trim}")
    if int(manifest.get("dpi") or 0) != DPI:
        failures.append(f"layout: dpi must be {DPI}")
    if manifest.get("bleed") is True:
        failures.append("layout: interior bleed is not authorized")
    if float(manifest.get("safe_margin_inches") or 0) < SAFE_MARGIN_INCHES:
        failures.append("layout: safe_margin_inches must be >= 0.50")

    canon_bound_count = 0
    try:
        all_canons = load_all_canons()
    except CanonError as exc:
        all_canons = {}
        failures.append(f"canon: {exc}")
    expected_canon_ids = list(manifest.get("canon_ids") or [])
    if len(expected_canon_ids) != 8:
        failures.append(f"canon: book must lock 8 canon ids, got {expected_canon_ids}")
    for canon_id, record in all_canons.items():
        if record.get("license") != "public_domain":
            failures.append(f"canon: {canon_id} is not documented as public_domain")
        if record.get("child_paraphrase", "").strip() == record.get("source_text", "").strip():
            failures.append(f"canon: {canon_id} mixes paraphrase into source_text")
    for mission in missions:
        try:
            bind_mission_record(mission)
            canon_bound_count += 1
        except CanonError as exc:
            failures.append(f"canon: {mission.get('id')}: {exc}")
    all_canons_bound = canon_bound_count == 8 and len(all_canons) == 8

    unique_failures = uniqueness_failures(missions, pages)
    unique_ok = not unique_failures
    failures.extend(unique_failures)
    failures.extend(search_target_failures(missions))

    answer_failures = answer_key_linkage_failures(manifest_pages=pages, missions=missions)
    answer_ok = not answer_failures
    failures.extend(answer_failures)

    unfilled = [
        int(page["page"])
        for page in pages
        if page.get("artwork_status") in {"unfilled_slot", "placeholder_only"}
    ]
    placeholder_assets_present = bool(unfilled)
    if unfilled and len(unfilled) != TARGET_PAGE_COUNT:
        # Partial fill is allowed later; Phase A expects every slot unfilled.
        pass
    if any(page.get("artwork_status") == "accepted" for page in pages):
        failures.append("artwork: Phase A cannot contain accepted production artwork")

    paid_image_calls = paid_call_count() if paid_image_calls is None else int(paid_image_calls)
    if paid_image_calls != 0:
        failures.append(f"paid_image_calls must be 0, got {paid_image_calls}")
    if int(manifest.get("paid_image_calls_authorized") or 0) != 0:
        failures.append("manifest authorizes paid image calls; Phase A must keep the gate closed")

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

    interior_present = bool(interior_pdf and Path(interior_pdf).is_file())
    if interior_present:
        failures.append(
            "technical: a 48-page interior PDF is present in Phase A; that work belongs to Phase B"
        )

    blueprint_pass = not failures
    technical_pass = False
    if not interior_present:
        # No composed 48-page proof, so the technical factory gate stays closed.
        technical_pass = False
    production_pass = False
    if placeholder_assets_present or not interior_present:
        production_pass = False
    if production_pass:
        failures.append("production_pass claimed while placeholders or missing proof remain")
        blueprint_pass = False
        production_pass = False

    report = {
        "book_id": manifest.get("book_id") or json.loads(BOOK_RECORD.read_text()).get("book_id"),
        "phase": manifest.get("phase", "A"),
        "target_page_count": TARGET_PAGE_COUNT,
        "page_count": page_count,
        "paid_image_calls": paid_image_calls,
        "estimated_spend_usd": 0.0,
        "canon_bound_count": canon_bound_count,
        "all_canons_bound": all_canons_bound,
        "facing_page_parity_ok": facing_ok,
        "font_floors_ok": font_ok,
        "answer_key_linkage_ok": answer_ok,
        "unique_content_ok": unique_ok,
        "unfilled_art_slots": len(unfilled),
        "placeholder_assets_present": placeholder_assets_present,
        "interior_pdf_present": interior_present,
        "artwork_status_summary": "unfilled_slot" if placeholder_assets_present else "mixed",
        "image_client_mode": client["mode"],
        "paid_generation_gate_implemented": PAID_GENERATION_GATE_IMPLEMENTED,
        "blueprint_pass": blueprint_pass,
        "technical_pass": technical_pass,
        "production_pass": production_pass,
        "pass": production_pass,
        "failures": failures,
        "blockers": list(PHASE_B_BLOCKERS),
    }
    schema_path = SCHEMA_DIR / "full_book_qa.schema.json"
    if schema_path.is_file():
        report_errors = validate_instance(report, schema_path, label="full_book_qa")
        if report_errors:
            report["failures"] = failures + report_errors
            report["blueprint_pass"] = False
            report["technical_pass"] = False
            report["production_pass"] = False
            report["pass"] = False
    return report


def write_full_book_report(report: dict[str, Any], path: Path | None = None) -> Path:
    destination = path or (OUTPUT_DIR / "full_book_qa.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return destination


def export_page_map(manifest: dict[str, Any] | None = None, path: Path | None = None) -> Path:
    mapping = {str(number): page for number, page in page_map(manifest).items()}
    destination = path or (OUTPUT_DIR / "page_map.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    return destination
