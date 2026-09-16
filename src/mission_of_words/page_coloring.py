"""Integrated coloring pages. Mission 1 remains the 4-page prototype floor."""

from __future__ import annotations

from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words.proof import live_box
from mission_of_words.scenes import draw_coloring_scene
from mission_of_words.templates import draw_activity_header, draw_panel, place_raster


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
    artwork_path: Path | None = None,
) -> dict:
    page = mission["pages"][0]
    box = live_box(page_number) if marked_proof else None
    plan = draw_activity_header(
        c,
        page_number,
        mission_number=int(mission.get("sequence") or 1),
        mission_title=str(mission.get("title") or ""),
        activity_title=page["title"],
        reference=str(canon.get("reference") or mission.get("scripture_reference") or ""),
        activity_label="Color this picture",
        instruction=page["child_instruction"],
        hero=True,
        box=box,
    )
    left, bottom, right, top = plan.art_box
    drawn: list[str]
    raster_meta: dict = {}
    if artwork_path and Path(artwork_path).is_file():
        draw_panel(c, plan.art_box, radius=10, width=1.6)
        inset = (left + 8, bottom + 8, right - 8, top - 8)
        raster_meta = place_raster(c, Path(artwork_path), inset, plan.state, name="hero_art")
        drawn = list(page["required_objects"])
        if "hero_scene" not in drawn:
            drawn.append("hero_scene")
        placeholder = False
        artwork_status = "accepted"
        integration = (
            "Hero coloring scene is a full-bleed line-art illustration inside the "
            "measured art window. Titles and instructions are code-rendered above it."
        )
    else:
        drawn = draw_coloring_scene(c, mission["id"], plan.art_box)
        placeholder = marked_proof
        artwork_status = "placeholder_only" if marked_proof else "procedural_lineart"
        integration = (
            "Single composed scene. Required objects are drawn in place, "
            "not patched onto a blank frame."
        )
    record = {
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
        **plan.state.as_fields(),
        **raster_meta,
    }
    return record


def draw_coloring_page(c: canvas.Canvas, spec: dict, canon: dict) -> dict:
    return draw_mission_coloring_page(c, _mission_from_spec(spec), canon, page_number=1)
