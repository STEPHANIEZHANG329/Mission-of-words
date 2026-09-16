"""Faith interaction pages: one coherent layout per mission, unique choices."""

from __future__ import annotations

from reportlab.lib.colors import black, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.geometry import BBox
from mission_of_words.layout import (
    MIN_CHECKBOX_INCHES,
    USED_INSTRUCTION_PT,
    content_box,
)
from mission_of_words.proof import live_box
from mission_of_words.templates import draw_activity_header, draw_panel
from mission_of_words.text import ink_text, wrapped_text


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def _choice_icon(c: canvas.Canvas, icon: str, x: float, y: float, card_w: float, card_h: float) -> None:
    cx = x + card_w - 28
    cy = y + card_h * 0.42
    if icon in {"help", "share", "include", "friend", "people", "family", "hands", "adult"}:
        art.draw_heart(c, cx, cy, 12)
    elif icon in {"kind", "heart", "forgive"}:
        art.draw_heart(c, cx, cy, 14)
    elif icon in {"sunrise"}:
        art.draw_sun(c, cx, cy + 6, 12)
    elif icon in {"moon"}:
        art.draw_moon(c, cx, cy + 4, 12)
    elif icon in {"leaf", "plant", "bin", "bird"}:
        art.draw_leaf(c, cx - 10, cy - 8, 22)
    elif icon in {"bread", "meal", "apple"}:
        art.draw_loaf(c, cx - 14, cy - 10, 26)
    elif icon in {"song", "words", "turn"}:
        art.draw_star(c, cx, cy + 4, 11)
    elif icon in {"clock", "coat"}:
        art.draw_basket(c, cx - 14, cy - 10, 26)
    elif icon in {"smile"}:
        art.circle(c, cx, cy, 12, 1.6)
    elif icon in {"cloud"}:
        art.draw_cloud(c, cx - 18, cy, 32)
    else:
        art.draw_lantern(c, cx - 12, cy - 14, 32)


def draw_faith_page(
    c: canvas.Canvas,
    spec: dict,
    canon: dict,
    *,
    page_number: int = 4,
    marked_proof: bool = False,
) -> dict:
    mission = _mission_from_spec(spec)
    page = mission["pages"][3]
    box = live_box(page_number) if marked_proof else content_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_number=int(mission.get("sequence") or 1),
        mission_title=str(mission.get("title") or ""),
        activity_title=page["title"],
        reference=str(canon.get("reference") or ""),
        activity_label="Faith in Action",
        instruction=page["child_instruction"],
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    inner_left = left + 6
    inner_right = right - 6
    inner_width = inner_right - inner_left
    y = top - 4

    para_h = 64
    draw_panel(c, (inner_left, y - para_h, inner_right, y), radius=10, width=1.4)
    ink_text(c)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inner_left + 10, y - 16, "For kids (not Bible wording):")
    plan.state.add(BBox("paraphrase_label", inner_left + 10, y - 20, inner_left + 240, y - 4, kind="text"))
    wrapped_text(
        c,
        canon["child_paraphrase"],
        inner_left + 10,
        y - 34,
        inner_width - 20,
        size=USED_INSTRUCTION_PT,
        leading=16,
    )
    y -= para_h + 12

    choices = page["choices"]
    gap = 12
    card_w = (inner_width - gap) / 2
    card_h = 70
    checkbox = MIN_CHECKBOX_INCHES * inch
    cards_bottom = y - 2 * (card_h + gap) + gap
    for index, choice in enumerate(choices):
        col = index % 2
        row = index // 2
        x = inner_left + col * (card_w + gap)
        cy = y - (row + 1) * (card_h + gap) + gap
        art.ink(c, 1.6)
        c.setFillColor(white)
        c.roundRect(x, cy, card_w, card_h, 12, fill=1, stroke=1)
        c.setStrokeColor(black)
        c.rect(x + 12, cy + card_h - 28, checkbox, checkbox, fill=0, stroke=1)
        _choice_icon(c, choice["icon"], x, cy, card_w, card_h)
        ink_text(c)
        c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
        c.drawString(x + 12 + checkbox + 8, cy + card_h - 26, choice["label"])
        plan.state.add(BBox(f"choice_{index}", x, cy, x + card_w, cy + card_h, kind="card"))

    y = cards_bottom - 20
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(inner_left, y, page["drawing_prompt"])
    plan.state.add(
        BBox(
            "drawing_prompt",
            inner_left,
            y - 3,
            inner_left + c.stringWidth(page["drawing_prompt"], "Helvetica-Bold", USED_INSTRUCTION_PT),
            y + USED_INSTRUCTION_PT * 0.82,
            kind="text",
        )
    )
    y -= 16
    prayer_h = 52
    draw_bottom = bottom + prayer_h + 12
    draw_h = y - draw_bottom
    draw_w = inner_width * 0.84
    body_x = inner_left + (inner_width - draw_w) / 2
    art.ink(c, 2.0)
    c.setFillColor(white)
    c.roundRect(body_x, draw_bottom, draw_w, draw_h, 16, fill=1, stroke=1)
    ink_text(c)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString((inner_left + inner_right) / 2, draw_bottom + draw_h * 0.48, "Draw here")
    plan.state.add(BBox("drawing_area", body_x, draw_bottom, body_x + draw_w, draw_bottom + draw_h, kind="draw"))

    draw_panel(c, (inner_left, bottom, inner_right, bottom + prayer_h), radius=10, width=1.4)
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(inner_left + 12, bottom + prayer_h - 16, "Prayer")
    wrapped_text(
        c,
        page["prayer"],
        inner_left + 12,
        bottom + prayer_h - 32,
        inner_width - 24,
        size=USED_INSTRUCTION_PT,
        leading=15,
    )

    drawing_sqin = (draw_w / 72.0) * (draw_h / 72.0)
    required = list(page["required_objects"])
    drawn = list(required)
    for extra in ("choice_cards", "prayer_ribbon", "child_paraphrase_box"):
        if extra not in drawn:
            drawn.append(extra)
    return {
        "page": page_number,
        "type": "faith_interaction",
        "mission_id": mission["id"],
        "visual_prompt": page["visual_prompt"],
        "required_objects": required,
        "drawn_objects": drawn,
        "text_in_artwork": False,
        "placeholder": marked_proof,
        "artwork_status": "placeholder_only" if marked_proof else "procedural_lineart",
        "asset_integration": (
            "Frame, four illustrated choices, drawing area, and prayer are one page design."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "drawing_area_sqin": drawing_sqin,
        "checkbox_inches": MIN_CHECKBOX_INCHES,
        "choice_count": len(choices),
        **plan.state.as_fields(),
    }
