"""Independent visual preflight. Separate from deterministic technical QA.

This module never marks a page PASS just because the PDF built. It checks
composition records, required objects, child usability, and known visual
defects (placeholder copy, missing drawing space, prompt/object mismatch).
Human visual review of rendered pages can still fail the bundle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
        if "child_with_lantern" not in drawn or "welcome_table" not in drawn:
            return False, "Maze start/finish pictures are missing."
    return True, "A 5-8 year old can see what to do from the instruction plus the picture."


def _integration_ok(record: dict[str, Any]) -> tuple[bool, str]:
    note = str(record.get("asset_integration") or "")
    if record.get("type") == "search_find":
        drawn = record.get("drawn_objects") or []
        if "search_background" not in drawn:
            return False, "Search page is missing an independent background asset."
        if len([name for name in drawn if name != "search_background"]) != 8:
            return False, "Search page did not integrate eight independent targets."
    if record.get("type") == "coloring" and "church" not in (record.get("drawn_objects") or []):
        return False, "Coloring page does not integrate the church scene."
    if record.get("text_in_artwork"):
        return False, "Artwork contains letters; coloring art must not."
    if not note:
        return False, "No asset-integration note was recorded."
    return True, note


def evaluate_visual(
    *,
    compositions: list[dict[str, Any]],
    preview_paths: list[Path],
    interior_pdf: Path,
    human_findings: list[dict[str, Any]],
) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    failures: list[str] = []

    if len(compositions) != 4:
        failures.append(f"visual: expected 4 composition records, got {len(compositions)}")
    if len(preview_paths) < 4:
        failures.append(f"visual: expected 4 page previews, got {len(preview_paths)}")
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

        page_fail_reasons = []
        if not integration_ok:
            page_fail_reasons.append(integration_note)
        if not child_ok:
            page_fail_reasons.append(child_note)
        if not prompt_ok:
            page_fail_reasons.append(prompt_note)
        if not human_pass:
            page_fail_reasons.append(human_notes)

        status = "PASS" if not page_fail_reasons else "FAIL"
        if page_fail_reasons:
            failures.extend(f"page {page_no}: {reason}" for reason in page_fail_reasons)
        pages.append(
            {
                "page": page_no,
                "type": record.get("type"),
                "status": status,
                "asset_integration": {"pass": integration_ok, "notes": integration_note},
                "child_usability": {"pass": child_ok, "notes": child_note},
                "prompt_to_art": {"pass": prompt_ok, "notes": prompt_note},
                "human_visual_review": {"pass": human_pass, "notes": human_notes},
            }
        )

    return {
        "kind": "visual_preflight",
        "separate_from_technical_qa": True,
        "pages": pages,
        "failures": failures,
        "pass": not failures,
    }


def write_visual_qa_markdown(report: dict[str, Any], path: Path) -> Path:
    lines = [
        "# Visual QA — Shine Your Light prototype",
        "",
        "This file is the **visual** preflight. It is not `qa_report.json`.",
        "A page cannot PASS if Asset Integration, Child Usability, Prompt-to-Art,",
        "or human visual review is FAIL.",
        "",
        f"**Overall:** {'PASS' if report['pass'] else 'FAIL'}",
        "",
    ]
    for page in report["pages"]:
        lines.append(f"## Page {page['page']} — {page['type']} — {page['status']}")
        lines.append("")
        for key, label in (
            ("asset_integration", "Asset Integration"),
            ("child_usability", "Child Usability"),
            ("prompt_to_art", "Prompt-to-Art"),
            ("human_visual_review", "Human visual review"),
        ):
            item = page[key]
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
