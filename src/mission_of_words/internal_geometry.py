"""INTERNAL engineering geometry mocks. Not an Owner-facing product.

Uses the rebuilt factory page composers so PM can review architecture
without treating procedural stand-in art as publication plates.
Paid GPT2 stays closed.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words.bible import bind_mission_record
from mission_of_words.book_manifest import load_book_record, load_mission_records
from mission_of_words.composition import (
    art_ratio,
    hero_art_ratio_bounds,
    maze_path_min_ratio,
    search_legend_height,
    validate_bibles,
)
from mission_of_words.layout import PAGE_H, PAGE_W
from mission_of_words.maze import generate_maze
from mission_of_words.page_back import (
    draw_answer_key_page,
    draw_certificate,
    draw_closing_page,
    draw_gratitude_journal,
    draw_prayer_walk,
)
from mission_of_words.page_coloring import draw_mission_coloring_page
from mission_of_words.page_faith import draw_faith_page
from mission_of_words.page_front import draw_contents_page, draw_parent_note_page, draw_title_page, draw_welcome_page
from mission_of_words.page_maze import draw_maze_page
from mission_of_words.page_search import build_search_scene_from_page, draw_search_find_page
from mission_of_words.proof import INTERNAL_LINE, INTERNAL_MARK, draw_internal_stamp
from mission_of_words.render import contact_sheet_grid, render_pdf_pages
from mission_of_words.templates import measure_activity_header

OUT = Path("output/internal_engineering_geometry")
PDF = OUT / "LittleLampkeepers_INTERNAL_ENGINEERING_GeometryOnly.pdf"
REPORT = OUT / "layout_report.json"
PREVIEWS = OUT / "previews"


def _hero_ratio(mission: dict, canon: dict, page_number: int) -> float:
    page = mission["pages"][0]
    plan = measure_activity_header(
        page_number,
        mission_number=int(mission.get("sequence") or 1),
        mission_title=str(mission.get("title") or ""),
        activity_title=page["title"],
        reference=str(canon.get("reference") or ""),
        activity_label="Color this picture",
        instruction=page["child_instruction"],
        hero=True,
    )
    return plan.art_height_ratio()


def build() -> dict:
    defects = validate_bibles()
    if defects:
        raise SystemExit("COMPOSITION_BIBLE_INVALID: " + "; ".join(defects))

    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    book = load_book_record()
    missions = load_mission_records()
    canons = {mission["id"]: bind_mission_record(mission) for mission in missions}
    runtime: dict[str, dict] = {}
    asset_root = OUT / "assets"
    for mission in missions:
        dest = asset_root / mission["id"]
        composed, search_manifest, _records = build_search_scene_from_page(
            mission["pages"][1],
            dest,
            page_number=int(mission["global_page_start"]) + 1,
            theme=mission["id"],
            marked_proof=False,
            status="procedural_lineart",
            mission=mission,
            canon=canons[mission["id"]],
        )
        maze_page = mission["pages"][2]
        rows, cols = maze_page["grid"]
        runtime[mission["id"]] = {
            "composed": composed,
            "search_manifest": search_manifest,
            "maze": generate_maze(rows=rows, cols=cols, seed=int(maze_page["seed"])),
            "asset_dir": dest,
        }

    c = canvas.Canvas(str(PDF), pagesize=(PAGE_W, PAGE_H))
    c.setTitle(INTERNAL_MARK)
    compositions: list[dict] = []

    def stamp(page: int) -> None:
        draw_internal_stamp(c, page)
        c.showPage()

    compositions.append(draw_title_page(c, book, 1))
    stamp(1)
    compositions.append(draw_welcome_page(c, book, 2))
    stamp(2)
    compositions.append(draw_contents_page(c, missions, 3))
    stamp(3)
    compositions.append(draw_parent_note_page(c, book, 4))
    stamp(4)

    for mission in missions:
        start = int(mission["global_page_start"])
        canon = canons[mission["id"]]
        pack = runtime[mission["id"]]
        compositions.append(
            draw_mission_coloring_page(c, mission, canon, page_number=start, marked_proof=False)
        )
        stamp(start)
        compositions.append(
            draw_search_find_page(
                c,
                mission,
                pack["composed"],
                pack["search_manifest"],
                page_number=start + 1,
                marked_proof=False,
                icon_dir=pack["asset_dir"],
                canon=canon,
            )
        )
        stamp(start + 1)
        compositions.append(
            draw_maze_page(
                c,
                mission,
                pack["maze"],
                page_number=start + 2,
                marked_proof=False,
                canon=canon,
            )
        )
        stamp(start + 2)
        compositions.append(draw_faith_page(c, mission, canon, page_number=start + 3, marked_proof=False))
        stamp(start + 3)

    for mission in missions:
        page_number = 36 + int(mission["sequence"])
        pack = runtime[mission["id"]]
        compositions.append(
            draw_answer_key_page(
                c,
                page_number=page_number,
                mission=mission,
                canon=canons[mission["id"]],
                search_composed=pack["composed"],
                search_manifest=pack["search_manifest"],
                maze=pack["maze"],
            )
        )
        stamp(page_number)

    compositions.append(draw_gratitude_journal(c, 45))
    stamp(45)
    compositions.append(draw_prayer_walk(c, 46))
    stamp(46)
    compositions.append(draw_certificate(c, book, 47))
    stamp(47)
    compositions.append(draw_closing_page(c, book, 48))
    stamp(48)
    c.save()

    previews = render_pdf_pages(PDF, PREVIEWS, dpi=110, prefix="page")
    contact = PREVIEWS / "contact_sheet.png"
    contact_sheet_grid(previews, contact, columns=6)

    lo, hi = hero_art_ratio_bounds()
    hero_ratios = {
        mission["id"]: round(_hero_ratio(mission, canons[mission["id"]], int(mission["global_page_start"])), 4)
        for mission in missions
    }
    maze_ratios = {
        record["mission_id"]: round(float(record.get("maze_path_ratio") or 0), 4)
        for record in compositions
        if record.get("type") == "maze"
    }
    report = {
        "status": "INTERNAL_ENGINEERING_ONLY",
        "paid_image_calls": 0,
        "page_count": len(previews),
        "trim_inches": [8.5, 11.0],
        "brand": "Little Lampkeepers",
        "consumer_title": "Little Lampkeepers: Shine Your Light This Fall",
        "proof_only": True,
        "owner_facing_product": False,
        "gpt2_allowed": False,
        "label": INTERNAL_LINE,
        "pdf": str(PDF),
        "contact_sheet": str(contact),
        "hero_art_ratio_bounds": [lo, hi],
        "hero_art_ratios": hero_ratios,
        "search_legend_pt": search_legend_height(),
        "maze_path_min_ratio": maze_path_min_ratio(),
        "maze_path_ratios": maze_ratios,
        "composition_ok": all(lo <= ratio <= hi for ratio in hero_ratios.values()),
        "stamp": INTERNAL_MARK,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    build()
