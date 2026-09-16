"""Faith interaction pages: illustrated activity sheets, not forms."""

from __future__ import annotations

from reportlab.lib.colors import black, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.composition import faith_drawing_min_sqin, faith_rhythm
from mission_of_words.fonts import FONT_BODY_BOLD, FONT_ITALIC
from mission_of_words.geometry import BBox
from mission_of_words.layout import (
    MIN_CHECKBOX_INCHES,
    USED_INSTRUCTION_PT,
    content_box,
)
from mission_of_words.proof import live_box
from mission_of_words.templates import draw_activity_header
from mission_of_words.text import ink_text, wrapped_text


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def _choice_icon(c: canvas.Canvas, icon: str, cx: float, cy: float, scale: float = 1.0) -> None:
    size = 22 * scale
    if icon in {"help", "share", "include", "friend", "people", "family", "hands", "adult", "kind", "heart", "forgive"}:
        art.draw_heart(c, cx, cy, 12 * scale)
    elif icon in {"sunrise"}:
        art.draw_sun(c, cx, cy + 4, 11 * scale)
    elif icon in {"moon"}:
        art.draw_moon(c, cx, cy + 2, 11 * scale)
    elif icon in {"leaf", "plant", "bin", "bird"}:
        art.draw_leaf(c, cx - 10, cy - 8, size)
    elif icon in {"bread", "meal", "apple"}:
        art.draw_loaf(c, cx - 12, cy - 8, 24 * scale)
    elif icon in {"song", "words", "turn"}:
        art.draw_star(c, cx, cy + 2, 10 * scale)
    elif icon in {"clock", "coat"}:
        art.draw_basket(c, cx - 12, cy - 8, 24 * scale)
    elif icon in {"smile"}:
        art.circle(c, cx, cy, 11 * scale, 1.6)
    elif icon in {"cloud"}:
        art.draw_cloud(c, cx - 16, cy, 28 * scale)
    else:
        art.draw_lantern(c, cx - 10, cy - 12, 28 * scale)


def _motif(c: canvas.Canvas, mission_id: str, box: tuple[float, float, float, float]) -> None:
    left, bottom, right, top = box
    if mission_id == "mission_02":
        art.draw_sun(c, left + 16, top - 18, 12)
        art.draw_moon(c, right - 22, top - 18, 10)
    elif mission_id == "mission_03":
        art.draw_wheat(c, left + 8, bottom + 8, 22)
        art.draw_wheat(c, right - 18, bottom + 8, 22)
    elif mission_id == "mission_04":
        art.draw_leaf(c, left + 8, top - 24, 18)
        art.draw_leaf(c, right - 26, bottom + 10, 18)
    elif mission_id == "mission_05":
        art.draw_basket(c, left + 8, bottom + 8, 22)
    elif mission_id == "mission_06":
        art.draw_star(c, left + 16, top - 14, 8)
        art.draw_star(c, right - 16, top - 14, 8)
    elif mission_id == "mission_07":
        art.draw_leaf(c, left + 10, bottom + 10, 16)
        art.draw_leaf(c, right - 24, top - 22, 16)
    elif mission_id == "mission_08":
        art.draw_loaf(c, (left + right) / 2 - 12, bottom + 8, 22)
    else:
        art.draw_lantern(c, (left + right) / 2 - 10, bottom + 8, 28)


def _card_boxes(
    rhythm: str,
    *,
    left: float,
    top: float,
    width: float,
    count: int,
) -> tuple[list[tuple[float, float, float, float]], float]:
    """Return card boxes and the y coordinate under the card block."""
    gap = 10
    boxes: list[tuple[float, float, float, float]] = []
    if rhythm in {"sky_strip", "porch_row", "creek_strip"}:
        card_w = (width - gap * (count - 1)) / count
        card_h = 78
        y = top - card_h
        for index in range(count):
            x = left + index * (card_w + gap)
            boxes.append((x, y, x + card_w, y + card_h))
        return boxes, y - 12
    if rhythm == "wagon_cluster":
        wide_h = 70
        y = top - wide_h
        half = (width - gap) / 2
        boxes.append((left, y, left + width, y + wide_h))
        y2 = y - gap - wide_h
        boxes.append((left, y2, left + half, y2 + wide_h))
        boxes.append((left + half + gap, y2, left + width, y2 + wide_h))
        y3 = y2 - gap - wide_h
        boxes.append((left, y3, left + width, y3 + wide_h))
        return boxes[:count], y3 - 12
    card_w = (width - gap) / 2
    card_h = 84
    for index in range(count):
        col = index % 2
        row = index // 2
        x = left + col * (card_w + gap)
        y = top - (row + 1) * (card_h + gap) + gap
        boxes.append((x, y, x + card_w, y + card_h))
    rows = (count + 1) // 2
    return boxes, top - rows * (card_h + gap) + gap - 12


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
    inner_left = left + 4
    inner_right = right - 4
    inner_width = inner_right - inner_left
    rhythm = faith_rhythm(mission["id"])

    ink_text(c)
    paraphrase = canon.get("child_paraphrase") or ""
    y = top - 2
    if paraphrase:
        y = wrapped_text(
            c,
            paraphrase,
            inner_left,
            y,
            inner_width,
            font=FONT_ITALIC,
            size=USED_INSTRUCTION_PT,
            leading=16,
        )
        plan.state.add(BBox("paraphrase", inner_left, y, inner_right, top, kind="text"))
        y -= 10

    choices = page["choices"]
    checkbox = MIN_CHECKBOX_INCHES * inch
    cards, y = _card_boxes(rhythm, left=inner_left, top=y, width=inner_width, count=len(choices))
    for index, (choice, card) in enumerate(zip(choices, cards)):
        x0, y0, x1, y1 = card
        card_w, card_h = x1 - x0, y1 - y0
        art.ink(c, 1.8)
        c.setFillColor(white)
        c.roundRect(x0, y0, card_w, card_h, 14, fill=1, stroke=1)
        _choice_icon(c, choice["icon"], x0 + 28, y0 + card_h * 0.52, scale=1.15)
        c.setStrokeColor(black)
        c.circle(x0 + 16, y0 + 16, checkbox / 2, fill=0, stroke=1)
        ink_text(c)
        c.setFont(FONT_BODY_BOLD, USED_INSTRUCTION_PT)
        label_x = x0 + 48
        wrapped_text(
            c,
            choice["label"],
            label_x,
            y0 + card_h - 22,
            card_w - 58,
            font=FONT_BODY_BOLD,
            size=USED_INSTRUCTION_PT,
            leading=15,
        )
        plan.state.add(BBox(f"choice_{index}", x0, y0, x1, y1, kind="card"))

    ink_text(c)
    c.setFont(FONT_BODY_BOLD, USED_INSTRUCTION_PT)
    c.drawString(inner_left, y, page["drawing_prompt"])
    plan.state.add(
        BBox(
            "drawing_prompt",
            inner_left,
            y - 3,
            inner_left + c.stringWidth(page["drawing_prompt"], FONT_BODY_BOLD, USED_INSTRUCTION_PT),
            y + USED_INSTRUCTION_PT * 0.82,
            kind="text",
        )
    )
    y -= 16
    prayer_h = 44
    draw_bottom = bottom + prayer_h + 10
    draw_h = y - draw_bottom
    draw_w = inner_width * 0.92
    body_x = inner_left + (inner_width - draw_w) / 2
    art.ink(c, 2.0)
    c.setFillColor(white)
    c.roundRect(body_x, draw_bottom, draw_w, draw_h, 18, fill=1, stroke=1)
    _motif(c, mission["id"], (body_x, draw_bottom, body_x + draw_w, draw_bottom + draw_h))
    ink_text(c)
    c.setFont(FONT_ITALIC, 11)
    c.drawCentredString((inner_left + inner_right) / 2, draw_bottom + 14, "Draw here")
    plan.state.add(BBox("drawing_area", body_x, draw_bottom, body_x + draw_w, draw_bottom + draw_h, kind="draw"))

    ink_text(c)
    c.setFont(FONT_BODY_BOLD, USED_INSTRUCTION_PT)
    c.drawString(inner_left, bottom + prayer_h - 14, "Prayer")
    wrapped_text(
        c,
        page["prayer"],
        inner_left + 64,
        bottom + prayer_h - 14,
        inner_width - 70,
        size=USED_INSTRUCTION_PT,
        leading=15,
    )

    drawing_sqin = (draw_w / 72.0) * (draw_h / 72.0)
    if drawing_sqin < faith_drawing_min_sqin():
        plan.state.overflow.append(
            f"faith drawing area {drawing_sqin:.1f} sq in is below {faith_drawing_min_sqin()}"
        )
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
            f"Illustrated {rhythm.replace('_', ' ')} choice cards, drawing area, and prayer — not a form."
        ),
        "faith_rhythm": rhythm,
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "drawing_area_sqin": drawing_sqin,
        "checkbox_inches": MIN_CHECKBOX_INCHES,
        "choice_count": len(choices),
        **plan.state.as_fields(),
    }
