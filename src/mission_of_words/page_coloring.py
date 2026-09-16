"""Integrated coloring pages. Mission 1 remains the 4-page prototype floor."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words.proof import live_box
from mission_of_words.scenes import draw_coloring_scene
from mission_of_words.text import page_header


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def draw_mission_coloring_page(
    c: canvas.Canvas,
    mission: dict,
    canon: dict,
    *,
    page_number: int,
    marked_proof: bool = False,
    accepted_image: Path | None = None,
) -> dict:
    page = mission["pages"][0]
    box = live_box(page_number) if marked_proof else None
    content, y = page_header(
        c,
        page_number,
        page["title"],
        page["child_instruction"],
        kicker=f"{canon['reference']}  ·  Color this picture",
        box=box,
    )
    left, bottom, right, top = content
    art_top = min(y, top - 72)
    art_bottom = bottom + 8
    if accepted_image is not None:
        c.drawImage(
            ImageReader(str(accepted_image)),
            left,
            art_bottom,
            width=right - left,
            height=art_top - art_bottom,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        drawn = list(page["required_objects"])
        artwork_status = "accepted"
        placeholder = False
        integration = (
            "Accepted coloring hero ingested into the live art box. "
            "Titles and instructions remain code-rendered."
        )
    else:
        drawn = draw_coloring_scene(c, mission["id"], (left, art_bottom, right, art_top))
        artwork_status = "placeholder_only" if marked_proof else "procedural_lineart"
        placeholder = marked_proof
        integration = (
            "Single composed scene. Required objects are drawn in place, "
            "not patched onto a blank frame."
        )
    return {
        "page": page_number,
        "type": "coloring",
        "mission_id": mission["id"],
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": drawn,
        "text_in_artwork": False,
        "placeholder": placeholder,
        "artwork_status": artwork_status,
        "asset_integration": integration,
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "drawing_area_sqin": None,
    }


def draw_coloring_page(c: canvas.Canvas, spec: dict, canon: dict) -> dict:
    return draw_mission_coloring_page(c, _mission_from_spec(spec), canon, page_number=1)
