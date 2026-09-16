"""48-page book manifest assembly and page-map helpers.

Mission records own activity content. Front/back matter records own those
pages. This module stitches them into the committed `book_manifest.json`
and checks that the map cannot drift from the source records.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from mission_of_words.layout import (
    INNER_SAFETY_INCHES,
    MIN_ANSWER_KEY_PT,
    MIN_INSTRUCTION_PT,
    MIN_PUZZLE_LETTER_PT,
    OUTER_SAFETY_INCHES,
    SAFE_MARGIN_INCHES,
    TRIM_INCHES,
)
from mission_of_words.paths import (
    BACK_MATTER,
    BOOK_MANIFEST,
    BOOK_RECORD,
    FRONT_MATTER,
    MISSIONS_DIR,
)

TARGET_PAGE_COUNT = 48
FRONT_PAGES = (1, 4)
MISSION_PAGES = (5, 36)
BACK_PAGES = (37, 48)
MISSION_SLOTS = ("A", "B", "C", "D")
MISSION_PAGE_TYPES = ("coloring", "search_find", "maze", "faith_interaction")
ANSWER_KEY_FIRST_PAGE = 37


class ManifestError(ValueError):
    """Raised when the 48-page map cannot be assembled or does not match."""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def facing_parity(page_number: int) -> dict[str, str]:
    if page_number < 1:
        raise ManifestError(f"page_number must be >= 1, got {page_number}")
    if page_number % 2 == 1:
        return {"facing": "recto", "parity": "odd"}
    return {"facing": "verso", "parity": "even"}


def apply_facing(page: dict[str, Any]) -> dict[str, Any]:
    record = dict(page)
    record.update(facing_parity(int(record["page"])))
    return record


def load_book_record(path: Path | None = None) -> dict[str, Any]:
    return _load_json(path or BOOK_RECORD)


def load_front_matter(path: Path | None = None) -> list[dict[str, Any]]:
    payload = _load_json(path or FRONT_MATTER)
    return [apply_facing(page) for page in payload["pages"]]


def load_back_matter(path: Path | None = None) -> list[dict[str, Any]]:
    payload = _load_json(path or BACK_MATTER)
    return [apply_facing(page) for page in payload["pages"]]


def load_mission_records(missions_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = missions_dir or MISSIONS_DIR
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("mission_*.json")):
        records.append(_load_json(path))
    records.sort(key=lambda item: int(item["sequence"]))
    return records


def answer_key_page_for(sequence: int) -> int:
    if sequence < 1 or sequence > 8:
        raise ManifestError(f"mission sequence must be 1-8, got {sequence}")
    return ANSWER_KEY_FIRST_PAGE + sequence - 1


def mission_pages_to_book_pages(mission: dict[str, Any]) -> list[dict[str, Any]]:
    sequence = int(mission["sequence"])
    start = int(mission["global_page_start"])
    expected_start = 5 + (sequence - 1) * 4
    if start != expected_start:
        raise ManifestError(
            f"{mission['id']} global_page_start must be {expected_start}, got {start}"
        )
    pages = list(mission.get("pages") or [])
    if len(pages) != 4:
        raise ManifestError(f"{mission['id']} must have exactly 4 pages")
    book_pages: list[dict[str, Any]] = []
    for index, page in enumerate(pages, start=1):
        if int(page["page"]) != index:
            raise ManifestError(
                f"{mission['id']} local page {page.get('page')} must be {index}"
            )
        expected_type = MISSION_PAGE_TYPES[index - 1]
        if page.get("type") != expected_type:
            raise ManifestError(
                f"{mission['id']} page {index} must be {expected_type}, got {page.get('type')}"
            )
        global_page = start + index - 1
        answer_page = answer_key_page_for(sequence) if expected_type in {"search_find", "maze"} else None
        record = {
            "page": global_page,
            "section": "missions",
            "type": page["type"],
            "title": page["title"],
            "mission_id": mission["id"],
            "mission_sequence": sequence,
            "mission_slot": MISSION_SLOTS[index - 1],
            "canon_id": mission["canon_id"],
            "activity_mechanic": page.get("activity_mechanic") or f"{mission['id']}_{expected_type}",
            "art_roles": list(page.get("art_roles") or _default_art_roles(expected_type)),
            "artwork_status": "placeholder_only",
            "answer_key_page": answer_page,
            "answers_activity_pages": [],
            "answer_sources": [],
            "source_mission_page": index,
            "child_instruction_required": True,
            "notes": (
                f"Mission {sequence} slot {MISSION_SLOTS[index - 1]}. "
                "Final page text is rendered by code. Artwork is a marked "
                "NON-PRODUCTION placeholder in Phase B."
            ),
        }
        book_pages.append(apply_facing(record))
    return book_pages


def _default_art_roles(page_type: str) -> list[str]:
    return {
        "coloring": ["coloring_hero"],
        "search_find": ["search_background", "search_target"],
        "maze": ["maze_scene"],
        "faith_interaction": ["faith_frame"],
    }[page_type]


def build_manifest(
    *,
    book: dict[str, Any] | None = None,
    front_pages: list[dict[str, Any]] | None = None,
    missions: list[dict[str, Any]] | None = None,
    back_pages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    book = deepcopy(book or load_book_record())
    front_pages = [apply_facing(page) for page in (front_pages or load_front_matter())]
    missions = missions or load_mission_records()
    back_pages = [apply_facing(page) for page in (back_pages or load_back_matter())]

    mission_book_pages: list[dict[str, Any]] = []
    for mission in missions:
        mission_book_pages.extend(mission_pages_to_book_pages(mission))

    pages = front_pages + mission_book_pages + back_pages
    pages.sort(key=lambda item: int(item["page"]))
    manifest = {
        "book_id": book["book_id"],
        "working_title": book["working_title"],
        "subtitle": book["subtitle"],
        "audience": book["audience"],
        "phase": book.get("phase", "B"),
        "target_page_count": TARGET_PAGE_COUNT,
        "trim_inches": list(book.get("trim_inches") or TRIM_INCHES),
        "dpi": int(book.get("dpi") or 300),
        "interior": book.get("interior", "black_and_white"),
        "bleed": bool(book.get("bleed", False)),
        "safe_margin_inches": float(book.get("safe_margin_inches") or SAFE_MARGIN_INCHES),
        "inner_safety_inches": float(book.get("inner_safety_inches") or INNER_SAFETY_INCHES),
        "outer_safety_inches": float(book.get("outer_safety_inches") or OUTER_SAFETY_INCHES),
        "min_instruction_pt": float(book.get("min_instruction_pt") or MIN_INSTRUCTION_PT),
        "min_puzzle_letter_pt": float(book.get("min_puzzle_letter_pt") or MIN_PUZZLE_LETTER_PT),
        "min_answer_key_pt": float(book.get("min_answer_key_pt") or MIN_ANSWER_KEY_PT),
        "kdp_list_price_usd": float(book.get("kdp_list_price_usd") or 9.99),
        "cover_status": book.get("cover_status", "deferred_until_interior_lock"),
        "paid_image_calls_authorized": 0,
        "mission_ids": list(book["mission_ids"]),
        "canon_ids": list(book["canon_ids"]),
        "sections": [
            {"name": "front_matter", "first_page": FRONT_PAGES[0], "last_page": FRONT_PAGES[1]},
            {"name": "missions", "first_page": MISSION_PAGES[0], "last_page": MISSION_PAGES[1]},
            {"name": "back_matter", "first_page": BACK_PAGES[0], "last_page": BACK_PAGES[1]},
        ],
        "pages": pages,
    }
    return manifest


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    return _load_json(path or BOOK_MANIFEST)


def write_manifest(manifest: dict[str, Any] | None = None, path: Path | None = None) -> Path:
    destination = path or BOOK_MANIFEST
    payload = manifest or build_manifest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def page_map(manifest: dict[str, Any] | None = None) -> dict[int, dict[str, Any]]:
    record = manifest or load_manifest()
    mapping: dict[int, dict[str, Any]] = {}
    for page in record["pages"]:
        number = int(page["page"])
        if number in mapping:
            raise ManifestError(f"duplicate page number {number}")
        mapping[number] = page
    return mapping


def manifest_consistency_errors(
    *,
    committed: dict[str, Any] | None = None,
    rebuilt: dict[str, Any] | None = None,
) -> list[str]:
    """Fail closed if the committed map drifts from assembled sources."""
    committed = committed or load_manifest()
    rebuilt = rebuilt or build_manifest()
    errors: list[str] = []
    if committed.get("pages") != rebuilt.get("pages"):
        errors.append("book_manifest.json pages do not match assembled front/mission/back records")
    skip = {"pages"}
    for key in rebuilt:
        if key in skip:
            continue
        if committed.get(key) != rebuilt.get(key):
            errors.append(f"book_manifest.json field {key} does not match assembled sources")
    return errors
