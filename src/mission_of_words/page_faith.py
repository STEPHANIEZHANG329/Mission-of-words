"""Page 4: one coherent faith interaction, not stacked fragments."""

from __future__ import annotations

from reportlab.lib.colors import black, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.layout import (
    MIN_CHECKBOX_INCHES,
    USED_INSTRUCTION_PT,
    USED_TITLE_PT,
    content_box,
)
from mission_of_words.text import ink_text, wrapped_text


def draw_faith_page(c: canvas.Canvas, spec: dict, canon: dict) -> dict:
    page = spec["mission"]["pages"][3]
    left, bottom, right, top = content_box(4)
    width = right - left

    # Outer lantern-shaped frame — the page is one object, all inside safety.
    frame_bottom = bottom + 4
    frame_top = top - 36
    frame_inset = 8
    cx = (left + right) / 2
    art.ink(c, 2.0)
    c.arc(cx - 26, frame_top + 6, cx + 26, top - 2, 0, 180)
    cap_w = width * 0.32
    art._path(
        c,
        [
            (cx - cap_w / 2, frame_top + 8),
            (cx + cap_w / 2, frame_top + 8),
            (cx + cap_w * 0.28, frame_top + 28),
            (cx - cap_w * 0.28, frame_top + 28),
        ],
        2.0,
        fill=1,
    )
    art.ink(c, 2.4)
    c.roundRect(
        left + frame_inset,
        frame_bottom,
        width - 2 * frame_inset,
        frame_top - frame_bottom,
        28,
        fill=0,
        stroke=1,
    )

    inner_left = left + 22
    inner_right = right - 22
    inner_width = inner_right - inner_left
    y = frame_top - 18

    ink_text(c)
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawCentredString(cx, y, page["title"])
    y -= 22
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, y, f"{canon['reference']}  ·  Bright Hearts")
    y -= 26

    # Paraphrase is labeled so it cannot be mistaken for Bible text.
    c.setFillColor(white)
    c.setStrokeColor(black)
    c.setLineWidth(1.4)
    para_h = 58
    c.roundRect(inner_left, y - para_h, inner_width, para_h, 10, fill=1, stroke=1)
    ink_text(c)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inner_left + 10, y - 16, "For kids (not Bible wording):")
    y = wrapped_text(
        c,
        canon["child_paraphrase"],
        inner_left + 10,
        y - 34,
        inner_width - 20,
        size=USED_INSTRUCTION_PT,
        leading=16,
    )
    y -= 18

    ink_text(c)
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(inner_left, y, page["child_instruction"])
    y -= 18

    # Four illustrated choices as one 2x2 panel, not a raw checklist.
    choices = page["choices"]
    gap = 10
    card_w = (inner_width - gap) / 2
    card_h = 78
    checkbox = MIN_CHECKBOX_INCHES * inch
    for index, choice in enumerate(choices):
        col = index % 2
        row = index // 2
        x = inner_left + col * (card_w + gap)
        cy = y - (row + 1) * (card_h + gap) + gap
        art.ink(c, 1.6)
        c.roundRect(x, cy, card_w, card_h, 12, fill=1, stroke=1)
        c.rect(x + 12, cy + card_h - 28, checkbox, checkbox, fill=0, stroke=1)
        icon_x = x + 16
        icon_y = cy + 8
        if choice["icon"] == "help":
            art.draw_child(c, icon_x + 22, icon_y, 44, facing=1, hair="bob", lantern=False)
            art.draw_basket(c, icon_x + 42, icon_y + 2, 26)
        elif choice["icon"] == "share":
            art.draw_child(c, icon_x + 18, icon_y, 42, facing=1, hair="short", lantern=False)
            art.draw_child(c, icon_x + 62, icon_y, 42, facing=-1, hair="bob", lantern=False)
            art.draw_apple(c, icon_x + 36, icon_y + 6, 20)
        elif choice["icon"] == "kind":
            art.draw_heart(c, x + card_w - 36, cy + 28, 18)
        else:
            art.draw_lantern(c, x + card_w - 50, cy + 8, 40)
        ink_text(c)
        c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
        c.drawString(x + 12 + checkbox + 8, cy + card_h - 26, choice["label"])

    y = y - 2 * (card_h + gap) - 8

    ink_text(c)
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(inner_left, y, page["drawing_prompt"])
    y -= 10
    draw_bottom = bottom + 78
    draw_h = y - draw_bottom
    draw_w = inner_width
    art.ink(c, 2.0)
    # lantern body as the drawing area
    body_x = inner_left + draw_w * 0.18
    body_w = draw_w * 0.64
    c.roundRect(body_x, draw_bottom + 8, body_w, draw_h - 28, 16, fill=1, stroke=1)
    art._path(
        c,
        [
            (body_x + body_w * 0.12, draw_bottom + draw_h - 20),
            (body_x + body_w * 0.88, draw_bottom + draw_h - 20),
            (body_x + body_w * 0.72, draw_bottom + draw_h + 4),
            (body_x + body_w * 0.28, draw_bottom + draw_h + 4),
        ],
        2.0,
        fill=1,
    )
    art.ink(c, 2.0)
    c.arc(
        cx - 26,
        draw_bottom + draw_h - 8,
        cx + 26,
        draw_bottom + draw_h + 28,
        0,
        180,
    )
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(black)
    c.drawCentredString(cx, draw_bottom + draw_h * 0.45, "Draw here")

    # Prayer ribbon
    art.ink(c, 1.6)
    c.roundRect(inner_left, bottom + 18, inner_width, 48, 10, fill=1, stroke=1)
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(inner_left + 12, bottom + 46, "Prayer")
    wrapped_text(
        c,
        page["prayer"],
        inner_left + 12,
        bottom + 28,
        inner_width - 24,
        size=USED_INSTRUCTION_PT,
        leading=15,
    )

    drawing_sqin = (body_w / 72.0) * ((draw_h - 28) / 72.0)
    return {
        "page": 4,
        "type": "faith_interaction",
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": [
            "lantern_frame",
            "choice_cards",
            "drawing_lantern",
            "prayer_ribbon",
            "child_paraphrase_box",
        ],
        "text_in_artwork": False,
        "asset_integration": (
            "Lantern frame, four illustrated choices, drawing lantern, and prayer "
            "are one page design."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "drawing_area_sqin": drawing_sqin,
        "checkbox_inches": MIN_CHECKBOX_INCHES,
        "choice_count": len(choices),
    }
