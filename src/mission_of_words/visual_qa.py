"""Independent visual preflight. Separate from deterministic technical QA.

This module never marks a page PASS just because the PDF built. It checks
composition records, required objects, child usability, and known visual
defects (placeholder copy, missing drawing space, prompt/object mismatch).
Human visual review of rendered pages can still fail the bundle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mission_of_words.art_bible import REQUIRED_QA_DIMENSIONS
from mission_of_words.layout import MIN_FAITH_DRAWING_SQIN, USED_INSTRUCTION_PT

PLACEHOLDER_NEEDLES = (
    "ARTWORK PLACEHOLDER",
    "placeholder_only",
    "TODO",
    "lorem ipsum",
)


def _objects_ok(record: dict[str, Any]) -> tuple[bool, str]:
    required = [str(item) for item in record.get("required_objects") or []]
    drawn = set(str(item) for item in record.get("drawn_objects") or [])
    missing = [item for item in required if item not in drawn]
    if missing:
        return False, f"Prompt-to-Art missing objects: {missing}"
    return True, "Required objects from the visual prompt are present in the composition."


def _child_ok(record: dict[str, Any]) -> tuple[bool, str]:
    instruction = str(record.get("child_instruction") or "").strip()
    if record.get("child_instruction_required") is False:
        return True, "No child instruction required on this page."
    if len(instruction) < 12:
        return False, "Child instruction is missing or too short for ages 5-8."
    if USED_INSTRUCTION_PT < 12:
        return False, "Instruction type is below 12pt."
    if record.get("type") == "faith_interaction":
        area = float(record.get("drawing_area_sqin") or 0)
        if area < MIN_FAITH_DRAWING_SQIN:
            return False, f"Drawing area {area:.1f} sq in is below {MIN_FAITH_DRAWING_SQIN}."
        if int(record.get("choice_count") or 0) < 4:
            return False, "Faith page needs four usable choices."
    if record.get("type") == "maze":
        drawn = set(record.get("drawn_objects") or [])
        required = set(record.get("required_objects") or [])
        missing_start_finish = [name for name in required if name not in drawn]
        if missing_start_finish:
            return False, f"Maze start/finish pictures are missing: {missing_start_finish}."
    return True, "A 5-8 year old can see what to do from the instruction plus the picture."


def _integration_ok(record: dict[str, Any]) -> tuple[bool, str]:
    note = str(record.get("asset_integration") or "")
    if record.get("type") == "search_find":
        drawn = record.get("drawn_objects") or []
        if "search_background" not in drawn:
            return False, "Search page is missing an independent background asset."
        if len([name for name in drawn if name != "search_background"]) != 8:
            return False, "Search page did not integrate eight independent targets."
    if record.get("text_in_artwork"):
        return False, "Artwork contains letters; coloring art must not."
    if not note:
        return False, "No asset-integration note was recorded."
    return True, note


def _dimension(record: dict[str, Any], human: dict[str, Any], name: str) -> tuple[bool, str]:
    if record.get("placeholder") or record.get("artwork_status") in {"unfilled_slot", "placeholder_only"}:
        return False, f"{name}: placeholder art cannot satisfy production visual QA."
    raw = human.get(name)
    if isinstance(raw, dict):
        return bool(raw.get("pass")), str(raw.get("notes") or "")
    if isinstance(raw, bool):
        return raw, "Human visual review recorded a boolean for this dimension."
    if isinstance(raw, str):
        return raw.upper() == "PASS", raw
    if name == "text_in_artwork":
        if record.get("text_in_artwork"):
            return False, "Artwork contains letters; coloring art must not."
        return True, "No letters recorded in the composition."
    if name == "coloring_usability":
        ok, note = _child_ok(record)
        return ok, note
    if name == "prompt_to_art":
        return _objects_ok(record)
    if name == "asset_integration":
        return _integration_ok(record)
    if name == "age_suitability":
        ok, note = _child_ok(record)
        return ok, note
    return False, f"{name}: not recorded; human visual review required."


def evaluate_visual(
    *,
    compositions: list[dict[str, Any]],
    preview_paths: list[Path],
    interior_pdf: Path,
    human_findings: list[dict[str, Any]],
    expected_pages: int = 4,
) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    failures: list[str] = []

    if len(compositions) != expected_pages:
        failures.append(f"visual: expected {expected_pages} composition records, got {len(compositions)}")
    if len(preview_paths) < expected_pages:
        failures.append(f"visual: expected {expected_pages} page previews, got {len(preview_paths)}")
    if not interior_pdf.is_file():
        failures.append("visual: interior PDF missing")

    human_by_page = {int(item["page"]): item for item in human_findings}

    for record in compositions:
        page_no = int(record["page"])
        integration_ok, integration_note = _integration_ok(record)
        child_ok, child_note = _child_ok(record)
        prompt_ok, prompt_note = _objects_ok(record)
        human = human_by_page.get(page_no, {})
        human_pass = bool(human.get("pass"))
        human_notes = str(human.get("notes") or "No human visual review recorded.")
        if not human:
            human_pass = False
            human_notes = "FAIL: visual review was not recorded for this page."
        page_fail_reasons: list[str] = []
        visual_readiness = "PASS"
        dimensions: dict[str, dict[str, Any]] = {}
        if record.get("placeholder") or record.get("artwork_status") in {
            "unfilled_slot",
            "placeholder_only",
        }:
            visual_readiness = "FAIL"
            page_fail_reasons.append(
                "MISSING/FAIL: placeholder or unfilled art cannot satisfy production visual readiness."
            )
        if not human_pass:
            visual_readiness = "MISSING" if visual_readiness == "PASS" else visual_readiness
        if not integration_ok:
            page_fail_reasons.append(integration_note)
        if not child_ok:
            page_fail_reasons.append(child_note)
        if not prompt_ok:
            page_fail_reasons.append(prompt_note)
        if not human_pass:
            page_fail_reasons.append(human_notes)
        for name in REQUIRED_QA_DIMENSIONS:
            dim_ok, dim_note = _dimension(record, human, name)
            dimensions[name] = {"pass": dim_ok, "notes": dim_note or name}
            if not dim_ok and visual_readiness == "PASS":
                visual_readiness = "FAIL"
                page_fail_reasons.append(dim_note)

        status = "PASS" if not page_fail_reasons else "FAIL"
        if page_fail_reasons:
            failures.extend(f"page {page_no}: {reason}" for reason in page_fail_reasons)
        pages.append(
            {
                "page": page_no,
                "type": record.get("type"),
                "status": status,
                "visual_readiness": visual_readiness,
                "asset_integration": {"pass": integration_ok, "notes": integration_note},
                "child_usability": {"pass": child_ok, "notes": child_note},
                "prompt_to_art": {"pass": prompt_ok, "notes": prompt_note},
                "human_visual_review": {"pass": human_pass, "notes": human_notes},
                "anatomy": dimensions.get("anatomy"),
                "line_consistency": dimensions.get("line_consistency"),
                "coloring_usability": dimensions.get("coloring_usability"),
                "composition": dimensions.get("composition"),
                "text_in_artwork": dimensions.get("text_in_artwork"),
                "age_suitability": dimensions.get("age_suitability"),
                "brand_consistency": dimensions.get("brand_consistency"),
            }
        )

    return {
        "kind": "visual_preflight",
        "separate_from_technical_qa": True,
        "expected_pages": expected_pages,
        "pages": pages,
        "failures": failures,
        "visual_readiness": "FAIL" if any(page.get("visual_readiness") != "PASS" for page in pages) or failures else "PASS",
        "pass": not failures,
    }


def evaluate_full_book_visual(
    *,
    compositions: list[dict[str, Any]],
    preview_paths: list[Path],
    interior_pdf: Path,
    human_findings: list[dict[str, Any]],
) -> dict[str, Any]:
    report = evaluate_visual(
        compositions=compositions,
        preview_paths=preview_paths,
        interior_pdf=interior_pdf,
        human_findings=human_findings,
        expected_pages=48,
    )
    report["kind"] = "full_book_visual_preflight"
    if report.get("visual_readiness") == "PASS":
        report["visual_readiness"] = "FAIL"
        report["failures"] = list(report["failures"]) + [
            "visual: 48-page technical proof cannot be production-ready while placeholder art remains"
        ]
        report["pass"] = False
    return report


def write_visual_qa_markdown(
    report: dict[str, Any],
    path: Path,
    *,
    title: str = "Visual QA — Shine Your Light prototype",
) -> Path:
    lines = [
        f"# {title}",
        "",
        "This file is the **visual** preflight. It is not `qa_report.json`.",
        "A page cannot PASS production visual readiness if Asset Integration,",
        "Child Usability, Prompt-to-Art, human visual review, or placeholder status is FAIL/MISSING.",
        "",
        f"**Overall:** {'PASS' if report['pass'] else 'FAIL'}",
        f"**Visual readiness:** {report.get('visual_readiness', 'FAIL' if not report['pass'] else 'PASS')}",
        "",
    ]
    for page in report["pages"]:
        readiness = page.get("visual_readiness") or page["status"]
        lines.append(f"## Page {page['page']} — {page['type']} — {page['status']} (visual readiness: {readiness})")
        lines.append("")
        for key, label in (
            ("asset_integration", "Asset Integration"),
            ("child_usability", "Child Usability"),
            ("prompt_to_art", "Prompt-to-Art"),
            ("human_visual_review", "Human visual review"),
            ("anatomy", "Anatomy"),
            ("line_consistency", "Line consistency"),
            ("coloring_usability", "Coloring usability"),
            ("composition", "Composition"),
            ("text_in_artwork", "Text-in-artwork"),
            ("age_suitability", "Age suitability"),
            ("brand_consistency", "Brand consistency"),
        ):
            item = page.get(key)
            if not item:
                continue
            mark = "PASS" if item["pass"] else "FAIL"
            lines.append(f"- **{label}:** {mark} — {item['notes']}")
        lines.append("")
    if report["failures"]:
        lines.append("## Failures")
        lines.append("")
        for failure in report["failures"]:
            lines.append(f"- {failure}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
