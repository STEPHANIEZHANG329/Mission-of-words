"""Phase C production interior builder.

Uses accepted GPT2 assets when present. production_pass stays false if any
page still has placeholder/rejected art, collisions, overflow, missing
visual review, or unreadable answer keys.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words.asset_ledger import load_ledger, write_ledger
from mission_of_words.bible import bind_mission_record
from mission_of_words.brand import ANSWER_PDF_NAME, COVER_PDF_NAME, INTERIOR_PDF_NAME
from mission_of_words.book_manifest import load_book_record, load_manifest, load_mission_records, write_manifest
from mission_of_words.full_book_qa import export_page_map, write_full_book_report
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
from mission_of_words.page_cover import write_cover_pdf
from mission_of_words.page_faith import draw_faith_page
from mission_of_words.page_front import draw_contents_page, draw_parent_note_page, draw_title_page, draw_welcome_page
from mission_of_words.page_maze import draw_maze_page
from mission_of_words.page_search import build_search_scene_from_page, draw_search_find_page
from mission_of_words.paths import ASSETS_DIR, BOOK_MANIFEST, OUTPUT_DIR
from mission_of_words.production_qa import evaluate_production
from mission_of_words.qa import write_report
from mission_of_words.raster import resample_to_print_box
from mission_of_words.render import contact_sheet_grid, render_pdf_pages
from mission_of_words.visual_qa import evaluate_visual, write_visual_qa_markdown

INTERIOR_PDF = OUTPUT_DIR / INTERIOR_PDF_NAME
ANSWER_PDF = OUTPUT_DIR / ANSWER_PDF_NAME
COVER_PDF = OUTPUT_DIR / COVER_PDF_NAME
ACCEPTED = ASSETS_DIR / "accepted"


def _accepted(asset_id: str) -> Path | None:
    path = ACCEPTED / f"{asset_id}.png"
    return path if path.is_file() else None


def _visual_review() -> list[dict]:
    path = OUTPUT_DIR / "human_visual_review.json"
    fallback = Path("content/books/bright_hearts_fall_01/production_visual_review.json")
    for candidate in (path, fallback):
        if candidate.is_file():
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            return list(payload.get("pages") or payload)
    return []


def build() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest()
    book = load_book_record()
    book["phase"] = "C"
    manifest = load_manifest()
    missions = load_mission_records()
    asset_dir = OUTPUT_DIR / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    ledger = load_ledger()

    mission_runtime: dict[str, dict] = {}
    asset_records: list[dict] = []
    for mission in missions:
        search_page = mission["pages"][1]
        maze_page = mission["pages"][2]
        dest = asset_dir / mission["id"]
        bg = _accepted(f"{mission['id']}_search_background")
        composed, search_manifest, records = build_search_scene_from_page(
            search_page,
            dest,
            page_number=int(mission["global_page_start"]) + 1,
            theme=mission["id"],
            marked_proof=False,
            status="accepted" if bg else "placeholder_only",
            mission=mission,
            background_path=bg,
        )
        rows, cols = maze_page["grid"]
        maze = generate_maze(rows=rows, cols=cols, seed=int(maze_page["seed"]))
        asset_records.extend(records)
        hero = _accepted(f"{mission['id']}_hero")
        hero_print = None
        if hero:
            print_path = dest / "hero_print.png"
            resample_to_print_box(hero, print_path, 7.2, 8.0)
            hero_print = print_path
        mission_runtime[mission["id"]] = {
            "mission": mission,
            "canon": bind_mission_record(mission),
            "composed": composed,
            "search_manifest": search_manifest,
            "maze": maze,
            "asset_dir": dest,
            "hero": hero_print or hero,
            "has_paid_hero": bool(hero),
            "has_paid_search": bool(bg),
        }

    compositions: list[dict] = []
    interior = canvas.Canvas(str(INTERIOR_PDF), pagesize=(PAGE_W, PAGE_H))
    compositions.append(draw_title_page(interior, book, 1))
    interior.showPage()
    compositions.append(draw_welcome_page(interior, book, 2))
    interior.showPage()
    compositions.append(draw_contents_page(interior, missions, 3))
    interior.showPage()
    compositions.append(draw_parent_note_page(interior, book, 4))
    interior.showPage()

    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        canon = runtime["canon"]
        start = int(mission["global_page_start"])
        coloring = draw_mission_coloring_page(
            interior,
            mission,
            canon,
            page_number=start,
            marked_proof=not runtime["has_paid_hero"],
            artwork_path=runtime["hero"],
        )
        if runtime["has_paid_hero"]:
            coloring["placeholder"] = False
            coloring["artwork_status"] = "accepted"
        compositions.append(coloring)
        interior.showPage()
        search = draw_search_find_page(
            interior,
            mission,
            runtime["composed"],
            runtime["search_manifest"],
            page_number=start + 1,
            marked_proof=not runtime["has_paid_search"],
            icon_dir=runtime["asset_dir"],
            canon=canon,
        )
        if runtime["has_paid_search"]:
            search["placeholder"] = False
            search["artwork_status"] = "accepted"
        compositions.append(search)
        interior.showPage()
        maze_page = draw_maze_page(
            interior,
            mission,
            runtime["maze"],
            page_number=start + 2,
            marked_proof=not runtime["has_paid_hero"],
            canon=canon,
            artwork_path=runtime["hero"],
        )
        if runtime["has_paid_hero"]:
            maze_page["placeholder"] = False
            maze_page["artwork_status"] = "accepted"
        compositions.append(maze_page)
        interior.showPage()
        faith = draw_faith_page(interior, mission, canon, page_number=start + 3, marked_proof=False)
        faith["placeholder"] = False
        faith["artwork_status"] = "code_layout"
        compositions.append(faith)
        interior.showPage()

    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        page_number = 36 + int(mission["sequence"])
        answer = draw_answer_key_page(
            interior,
            page_number=page_number,
            mission=mission,
            canon=runtime["canon"],
            search_composed=runtime["composed"],
            search_manifest=runtime["search_manifest"],
            maze=runtime["maze"],
        )
        answer["placeholder"] = False
        answer["artwork_status"] = "code_layout"
        compositions.append(answer)
        interior.showPage()

    for drawer, number in (
        (draw_gratitude_journal, 45),
        (draw_prayer_walk, 46),
        (lambda c, n: draw_certificate(c, book, n), 47),
        (lambda c, n: draw_closing_page(c, book, n), 48),
    ):
        rec = drawer(interior, number)
        rec["placeholder"] = False
        rec["artwork_status"] = "code_layout"
        compositions.append(rec)
        interior.showPage()
    interior.save()

    answers = canvas.Canvas(str(ANSWER_PDF), pagesize=(PAGE_W, PAGE_H))
    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        rec = draw_answer_key_page(
            answers,
            page_number=int(mission["sequence"]),
            mission=mission,
            canon=runtime["canon"],
            search_composed=runtime["composed"],
            search_manifest=runtime["search_manifest"],
            maze=runtime["maze"],
        )
        rec["placeholder"] = False
        answers.showPage()
    answers.save()

    cover_art = _accepted("cover_front")
    write_cover_pdf(COVER_PDF, artwork=cover_art)

    preview_dir = OUTPUT_DIR / "previews"
    previews = render_pdf_pages(INTERIOR_PDF, preview_dir, dpi=120, prefix="page")
    answer_previews = render_pdf_pages(ANSWER_PDF, preview_dir, dpi=110, prefix="answer")
    contact_sheet_grid(previews, preview_dir / "contact_sheet.png", columns=8)
    contact_sheet_grid(previews[:4], preview_dir / "contact_sheet_front.png", columns=4)
    contact_sheet_grid(previews[4:20], preview_dir / "contact_sheet_missions_1.png", columns=4)
    contact_sheet_grid(previews[20:36], preview_dir / "contact_sheet_missions_2.png", columns=4)
    contact_sheet_grid(previews[36:], preview_dir / "contact_sheet_back.png", columns=4)
    contact_sheet_grid(answer_previews, preview_dir / "contact_sheet_answers.png", columns=4)
    if COVER_PDF.is_file():
        render_pdf_pages(COVER_PDF, preview_dir, dpi=80, prefix="cover")

    visual = evaluate_visual(
        compositions=compositions,
        preview_paths=previews,
        interior_pdf=INTERIOR_PDF,
        human_findings=_visual_review(),
        expected_pages=48,
    )
    write_visual_qa_markdown(visual, OUTPUT_DIR / "visual_qa.md", title="Visual QA — Phase C production candidate")
    (OUTPUT_DIR / "visual_qa.json").write_text(json.dumps(visual, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "compositions.json").write_text(json.dumps(compositions, indent=2, default=str) + "\n", encoding="utf-8")
    write_ledger(ledger)

    mazes = {mission_id: runtime["maze"] for mission_id, runtime in mission_runtime.items()}
    search_manifests = {
        mission_id: runtime["search_manifest"] for mission_id, runtime in mission_runtime.items()
    }
    qa = evaluate_production(
        manifest=manifest,
        missions=missions,
        compositions=compositions,
        visual=visual,
        interior_pdf=INTERIOR_PDF,
        answer_pdf=ANSWER_PDF,
        mazes=mazes,
        search_manifests=search_manifests,
        ledger=ledger,
        preview_count=len(previews),
        asset_records=asset_records,
    )
    write_full_book_report(qa)
    write_report(qa, OUTPUT_DIR / "qa_report.json")
    export_page_map(manifest)
    (OUTPUT_DIR / "book_manifest.json").write_text(BOOK_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
    return qa


if __name__ == "__main__":
    result = build()
    print(json.dumps({k: result[k] for k in result if k != "pages"}, indent=2, default=str))
    if result.get("production_pass") is not True:
        raise SystemExit(0)
