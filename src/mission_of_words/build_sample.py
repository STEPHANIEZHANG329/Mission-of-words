from __future__ import annotations

import json
from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words.bible import bind_mission_canon
from mission_of_words.image_client import paid_call_count
from mission_of_words.layout import PAGE_H, PAGE_W
from mission_of_words.maze import generate_maze
from mission_of_words.page_coloring import draw_coloring_page
from mission_of_words.page_faith import draw_faith_page
from mission_of_words.page_maze import draw_maze_page
from mission_of_words.page_search import build_search_scene, draw_search_find_page
from mission_of_words.paths import MISSION_SPEC, OUTPUT_DIR, ROOT
from mission_of_words.qa import evaluate_build, write_report
from mission_of_words.render import contact_sheet, render_pdf_pages
from mission_of_words.visual_qa import evaluate_visual, write_visual_qa_markdown

INTERIOR_PDF = OUTPUT_DIR / "BrightHearts_ShineYourLight_Interior.pdf"
ANSWER_PDF = OUTPUT_DIR / "BrightHearts_ShineYourLight_AnswerKey.pdf"
ASSET_REGISTER = OUTPUT_DIR / "asset_register.json"
VISUAL_REVIEW = ROOT / "content" / "books" / "bright_hearts_fall_01" / "visual_review.json"


def load_spec() -> dict:
    return json.loads(MISSION_SPEC.read_text(encoding="utf-8"))


def _load_visual_review() -> list[dict]:
    if not VISUAL_REVIEW.is_file():
        return []
    payload = json.loads(VISUAL_REVIEW.read_text(encoding="utf-8"))
    return list(payload.get("pages") or [])


def build() -> dict:
    spec = load_spec()
    canon = bind_mission_canon(spec)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    asset_dir = OUTPUT_DIR / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)

    maze_page = spec["mission"]["pages"][2]
    rows, cols = maze_page["grid"]
    maze = generate_maze(rows=rows, cols=cols, seed=maze_page["seed"])

    composed, manifest, asset_records = build_search_scene(spec, asset_dir)
    ASSET_REGISTER.write_text(
        json.dumps(
            {
                "paid_image_calls": 0,
                "estimated_spend_usd": 0.0,
                "model": "procedural-lineart",
                "assets": asset_records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    compositions: list[dict] = []
    c = canvas.Canvas(str(INTERIOR_PDF), pagesize=(PAGE_W, PAGE_H))
    compositions.append(draw_coloring_page(c, spec, canon))
    c.showPage()
    compositions.append(
        draw_search_find_page(c, spec, composed, manifest, answer_key=False)
    )
    c.showPage()
    compositions.append(draw_maze_page(c, spec, maze))
    c.showPage()
    compositions.append(draw_faith_page(c, spec, canon))
    c.save()

    a = canvas.Canvas(str(ANSWER_PDF), pagesize=(PAGE_W, PAGE_H))
    draw_search_find_page(a, spec, composed, manifest, answer_key=True)
    a.showPage()
    draw_maze_page(a, spec, maze, answer_key=True, page_number=2)
    a.save()

    preview_dir = OUTPUT_DIR / "previews"
    previews = render_pdf_pages(INTERIOR_PDF, preview_dir, dpi=150, prefix="page")
    render_pdf_pages(ANSWER_PDF, preview_dir, dpi=130, prefix="answer")
    contact_sheet(previews, preview_dir / "contact_sheet.png")

    visual = evaluate_visual(
        compositions=compositions,
        preview_paths=previews,
        interior_pdf=INTERIOR_PDF,
        human_findings=_load_visual_review(),
    )
    write_visual_qa_markdown(visual, OUTPUT_DIR / "visual_qa.md")
    (OUTPUT_DIR / "visual_qa.json").write_text(json.dumps(visual, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "compositions.json").write_text(
        json.dumps(compositions, indent=2, default=str) + "\n", encoding="utf-8"
    )

    qa = evaluate_build(
        spec=spec,
        maze=maze,
        paid_image_calls=paid_call_count(),
        sample_pages=4,
        search_manifest=manifest,
        compositions=compositions,
        interior_pdf=INTERIOR_PDF,
        visual_qa_pass=visual["pass"],
        preview_count=len(previews),
        asset_records=asset_records,
    )
    write_report(qa)
    return qa


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(1)
