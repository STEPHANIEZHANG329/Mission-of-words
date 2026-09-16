"""48-page INTERNAL geometry-mock renderer.

This is not a product, commercial proof, or KDP candidate. Publication art
is forbidden until PM architecture review and a new Owner GPT2 grant.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words.bible import bind_mission_record, load_all_canons
from mission_of_words.bibles import validate_bibles
from mission_of_words.book_manifest import load_book_record, load_manifest, load_mission_records, write_manifest
from mission_of_words.brand import FORBIDDEN_CONSUMER_MARK, TITLE
from mission_of_words.full_book_qa import evaluate_full_book, export_page_map, write_full_book_report
from mission_of_words.image_client import paid_call_count
from mission_of_words.layout import PAGE_H, PAGE_W
from mission_of_words.maze import generate_maze
from mission_of_words.page_factory import (
    draw_answer_key_page,
    draw_certificate_page,
    draw_closing_page,
    draw_contents_page,
    draw_faith_page,
    draw_gratitude_page,
    draw_hero_page,
    draw_maze_page,
    draw_parent_note_page,
    draw_prayer_walk_page,
    draw_search_page,
    draw_title_page,
    draw_welcome_page,
)
from mission_of_words.page_search import build_search_scene_from_page
from mission_of_words.paths import BOOK_MANIFEST, OUTPUT_DIR
from mission_of_words.proof import (
    FORBIDDEN_PRODUCT_LABELS,
    INTERNAL_MOCK_MARK,
    draw_diagonal_watermark,
    draw_proof_mark,
)
from mission_of_words.qa import write_report
from mission_of_words.render import contact_sheet_grid, render_pdf_pages
from mission_of_words.typefaces import register
from mission_of_words.visual_qa import evaluate_full_book_visual, write_visual_qa_markdown

INTERIOR_PDF = OUTPUT_DIR / "INTERNAL_LittleLampkeepers_48_GeometryMocks_NOT_PRODUCT.pdf"
ANSWER_PDF = OUTPUT_DIR / "INTERNAL_LittleLampkeepers_AnswerKey_GeometryMocks_NOT_PRODUCT.pdf"
ASSET_REGISTER = OUTPUT_DIR / "asset_register.json"
ARCHITECTURE_REPORT = OUTPUT_DIR / "architecture_qa.json"


def _stamp(c: canvas.Canvas, page_number: int) -> None:
    draw_diagonal_watermark(c)
    draw_proof_mark(c, page_number)


def build() -> dict:
    register()
    bible_failures = validate_bibles()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest()
    book = load_book_record()
    book["phase"] = "architecture_reset"
    book["working_title"] = TITLE
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
            mission=mission,
            canon=bind_mission_record(mission),
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
    _stamp(interior, 1)
    interior.showPage()
    compositions.append(draw_welcome_page(interior, book, 2))
    _stamp(interior, 2)
    interior.showPage()
    compositions.append(draw_contents_page(interior, missions, 3))
    _stamp(interior, 3)
    interior.showPage()
    compositions.append(draw_parent_note_page(interior, book, 4))
    _stamp(interior, 4)
    interior.showPage()

    for mission in missions:
        runtime = mission_runtime[mission["id"]]
        canon = runtime["canon"]
        start = int(mission["global_page_start"])
        compositions.append(draw_hero_page(interior, mission, canon, start))
        _stamp(interior, start)
        interior.showPage()
        compositions.append(
            draw_search_page(
                interior,
                mission,
                canon,
                runtime["composed"],
                runtime["search_manifest"],
                start + 1,
            )
        )
        _stamp(interior, start + 1)
        interior.showPage()
        compositions.append(
            draw_maze_page(interior, mission, canon, runtime["maze"], start + 2)
        )
        _stamp(interior, start + 2)
        interior.showPage()
        compositions.append(draw_faith_page(interior, mission, canon, start + 3))
        _stamp(interior, start + 3)
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
        _stamp(interior, page_number)
        interior.showPage()

    compositions.append(draw_gratitude_page(interior, 45))
    _stamp(interior, 45)
    interior.showPage()
    compositions.append(draw_prayer_walk_page(interior, 46))
    _stamp(interior, 46)
    interior.showPage()
    compositions.append(draw_certificate_page(interior, book, 47))
    _stamp(interior, 47)
    interior.showPage()
    compositions.append(draw_closing_page(interior, book, 48))
    _stamp(interior, 48)
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
        _stamp(answers, page_number)
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
                "model": "none",
                "status": "placeholder_only",
                "owner_facing": False,
                "label": INTERNAL_MOCK_MARK,
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
        human_findings=[],
    )
    write_visual_qa_markdown(
        visual,
        OUTPUT_DIR / "visual_qa.md",
        title="Visual QA — INTERNAL geometry mocks (not product)",
    )
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
    if bible_failures:
        qa["failures"] = list(qa.get("failures") or []) + bible_failures
        qa["technical_pass"] = False
    qa["production_pass"] = False
    qa["pass"] = False
    write_full_book_report(qa)
    write_report(qa, OUTPUT_DIR / "qa_report.json")
    export_page_map(manifest)
    (OUTPUT_DIR / "book_manifest.json").write_text(BOOK_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
    ARCHITECTURE_REPORT.write_text(
        json.dumps(
            {
                "status": "PENDING_PM_REVIEW",
                "owner_facing": False,
                "production_pass": False,
                "paid_image_calls": 0,
                "interior_pdf": INTERIOR_PDF.name,
                "answer_pdf": ANSWER_PDF.name,
                "forbidden_product_labels": list(FORBIDDEN_PRODUCT_LABELS),
                "bible_failures": bible_failures,
                "gpt2_blockers": json.loads(
                    (Path(__file__).resolve().parents[2] / "ops" / "architecture_review.json").read_text()
                )["required_before_gpt2_reopen"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
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
    if FORBIDDEN_CONSUMER_MARK.encode() in INTERIOR_PDF.read_bytes():
        raise SystemExit("forbidden consumer mark in PDF")
    text_name = INTERIOR_PDF.name.upper()
    if "PRODUCT" not in text_name or "INTERNAL" not in text_name:
        raise SystemExit("geometry mock PDF must be labeled INTERNAL and NOT PRODUCT")
