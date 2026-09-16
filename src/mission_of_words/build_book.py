"""Deterministic 48-page Bright Hearts technical-proof renderer.

Phase B: unpaid procedural/placeholder art only. paid_image_calls stays 0.
production_pass stays false while placeholders remain.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words.bible import bind_mission_record, load_all_canons
from mission_of_words.book_manifest import load_book_record, load_manifest, load_mission_records, write_manifest
from mission_of_words.full_book_qa import evaluate_full_book, export_page_map, write_full_book_report
from mission_of_words.image_client import paid_call_count
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
from mission_of_words.paths import BOOK_MANIFEST, OUTPUT_DIR, ROOT
from mission_of_words.proof import NON_PRODUCTION_MARK, draw_proof_mark
from mission_of_words.qa import write_report
from mission_of_words.render import contact_sheet_grid, render_pdf_pages
from mission_of_words.visual_qa import evaluate_full_book_visual, write_visual_qa_markdown

INTERIOR_PDF = OUTPUT_DIR / "BrightHearts_Fall_Interior_TechnicalProof.pdf"
ANSWER_PDF = OUTPUT_DIR / "BrightHearts_Fall_AnswerKey_TechnicalProof.pdf"
ASSET_REGISTER = OUTPUT_DIR / "asset_register.json"
VISUAL_REVIEW = ROOT / "content" / "books" / "bright_hearts_fall_01" / "visual_review.json"


def _load_visual_review() -> list[dict]:
    if not VISUAL_REVIEW.is_file():
        return []
    payload = json.loads(VISUAL_REVIEW.read_text(encoding="utf-8"))
    return list(payload.get("pages") or [])


def build() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest()
    book = load_book_record()
    book["phase"] = "B"
    manifest = load_manifest()
    missions = load_mission_records()
    canons = load_all_canons()
    asset_dir = OUTPUT_DIR / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)

    mission_runtime: dict[str, dict] = {}
    asset_records: list[dict] = []
    for mission in missions:
        search_page = mission["pages"][1]
        maze_page = mission["pages"][2]
        dest = asset_dir / mission["id"]
        composed, search_manifest, records = build_search_scene_from_page(
            search_page,
            dest,
            page_number=int(mission["global_page_start"]) + 1,
            theme=mission["id"],
            marked_proof=True,
            status="placeholder_only",
        )
        rows, cols = maze_page["grid"]
        maze = generate_maze(rows=rows, cols=cols, seed=int(maze_page["seed"]))
        asset_records.extend(records)
        mission_runtime[mission["id"]] = {
            "mission": mission,
            "canon": bind_mission_record(mission),
            "composed": composed,
            "search_manifest": search_manifest,
            "maze": maze,
            "asset_dir": dest,
        }

    compositions: list[dict] = []
    interior = canvas.Canvas(str(INTERIOR_PDF), pagesize=(PAGE_W, PAGE_H))
    compositions.append(draw_title_page(interior, book, 1))
    draw_proof_mark(interior, 1)
    interior.showPage()
    compositions.append(draw_welcome_page(interior, book, 2))
    draw_proof_mark(interior, 2)
    interior.showPage()
    compositions.append(draw_contents_page(interior, missions, 3))
    draw_proof_mark(interior, 3)
    interior.showPage()
    compositions.append(draw_parent_note_page(interior, book, 4))
    draw_proof_mark(interior, 4)
    interior.showPage()

    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        canon = runtime["canon"]
        start = int(mission["global_page_start"])
        compositions.append(
            draw_mission_coloring_page(interior, mission, canon, page_number=start, marked_proof=True)
        )
        draw_proof_mark(interior, start)
        interior.showPage()
        compositions.append(
            draw_search_find_page(
                interior,
                mission,
                runtime["composed"],
                runtime["search_manifest"],
                page_number=start + 1,
                marked_proof=True,
                icon_dir=runtime["asset_dir"],
                canon=canon,
            )
        )
        draw_proof_mark(interior, start + 1)
        interior.showPage()
        compositions.append(
            draw_maze_page(
                interior,
                mission,
                runtime["maze"],
                page_number=start + 2,
                marked_proof=True,
                canon=canon,
            )
        )
        draw_proof_mark(interior, start + 2)
        interior.showPage()
        compositions.append(
            draw_faith_page(interior, mission, canon, page_number=start + 3, marked_proof=True)
        )
        draw_proof_mark(interior, start + 3)
        interior.showPage()

    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        page_number = 36 + int(mission["sequence"])
        compositions.append(
            draw_answer_key_page(
                interior,
                page_number=page_number,
                mission=mission,
                canon=runtime["canon"],
                search_composed=runtime["composed"],
                search_manifest=runtime["search_manifest"],
                maze=runtime["maze"],
            )
        )
        draw_proof_mark(interior, page_number)
        interior.showPage()

    compositions.append(draw_gratitude_journal(interior, 45))
    draw_proof_mark(interior, 45)
    interior.showPage()
    compositions.append(draw_prayer_walk(interior, 46))
    draw_proof_mark(interior, 46)
    interior.showPage()
    compositions.append(draw_certificate(interior, book, 47))
    draw_proof_mark(interior, 47)
    interior.showPage()
    compositions.append(draw_closing_page(interior, book, 48))
    draw_proof_mark(interior, 48)
    interior.save()

    answers = canvas.Canvas(str(ANSWER_PDF), pagesize=(PAGE_W, PAGE_H))
    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        page_number = int(mission["sequence"])
        draw_answer_key_page(
            answers,
            page_number=page_number,
            mission=mission,
            canon=runtime["canon"],
            search_composed=runtime["composed"],
            search_manifest=runtime["search_manifest"],
            maze=runtime["maze"],
        )
        draw_proof_mark(answers, page_number)
        answers.showPage()
    answers.save()

    preview_dir = OUTPUT_DIR / "previews"
    previews = render_pdf_pages(INTERIOR_PDF, preview_dir, dpi=120, prefix="page")
    answer_previews = render_pdf_pages(ANSWER_PDF, preview_dir, dpi=110, prefix="answer")
    contact_sheet_grid(previews, preview_dir / "contact_sheet.png", columns=8)
    contact_sheet_grid(previews[:4], preview_dir / "contact_sheet_front.png", columns=4)
    contact_sheet_grid(previews[4:20], preview_dir / "contact_sheet_missions_1.png", columns=4)
    contact_sheet_grid(previews[20:36], preview_dir / "contact_sheet_missions_2.png", columns=4)
    contact_sheet_grid(previews[36:], preview_dir / "contact_sheet_back.png", columns=4)
    contact_sheet_grid(answer_previews, preview_dir / "contact_sheet_answers.png", columns=4)

    ASSET_REGISTER.write_text(
        json.dumps(
            {
                "paid_image_calls": 0,
                "estimated_spend_usd": 0.0,
                "model": "procedural-lineart",
                "status": "placeholder_only",
                "non_production_mark": NON_PRODUCTION_MARK,
                "assets": asset_records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "compositions.json").write_text(
        json.dumps(compositions, indent=2, default=str) + "\n", encoding="utf-8"
    )

    visual = evaluate_full_book_visual(
        compositions=compositions,
        preview_paths=previews,
        interior_pdf=INTERIOR_PDF,
        human_findings=_load_visual_review(),
    )
    write_visual_qa_markdown(visual, OUTPUT_DIR / "visual_qa.md", title="Visual QA — 48-page technical proof")
    (OUTPUT_DIR / "visual_qa.json").write_text(json.dumps(visual, indent=2) + "\n", encoding="utf-8")

    mazes = {mission_id: runtime["maze"] for mission_id, runtime in mission_runtime.items()}
    search_manifests = {
        mission_id: runtime["search_manifest"] for mission_id, runtime in mission_runtime.items()
    }
    qa = evaluate_full_book(
        manifest=manifest,
        missions=missions,
        paid_image_calls=paid_call_count(),
        interior_pdf=INTERIOR_PDF,
        compositions=compositions,
        mazes=mazes,
        search_manifests=search_manifests,
        visual_readiness=visual.get("visual_readiness", "FAIL"),
        preview_count=len(previews),
        asset_records=asset_records,
        answer_pdf=ANSWER_PDF,
    )
    write_full_book_report(qa)
    write_report(qa, OUTPUT_DIR / "qa_report.json")
    export_page_map(manifest)
    (OUTPUT_DIR / "book_manifest.json").write_text(BOOK_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
    return qa


if __name__ == "__main__":
    result = build()
    print(json.dumps({k: result[k] for k in result if k != "pages"}, indent=2, default=str))
    if result["paid_image_calls"] != 0:
        raise SystemExit(1)
    if result["production_pass"] is True or result["pass"] is True:
        raise SystemExit(1)
    if result["technical_pass"] is not True:
        raise SystemExit(1)
