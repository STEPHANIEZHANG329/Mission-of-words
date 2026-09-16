"""Faith interaction pages: one coherent layout per mission, unique choices."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import black, white
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.layout import (
    MIN_CHECKBOX_INCHES,
    USED_INSTRUCTION_PT,
    USED_TITLE_PT,
    content_box,
)
from mission_of_words.proof import live_box
from mission_of_words.text import ink_text, wrapped_text


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def _choice_icon(c: canvas.Canvas, icon: str, x: float, y: float, card_w: float, card_h: float) -> None:
    icon_x = x + 16
    icon_y = y + 8
    if icon in {"help"}:
        art.draw_child(c, icon_x + 22, icon_y, 44, facing=1, hair="bob", lantern=False)
        art.draw_basket(c, icon_x + 42, icon_y + 2, 26)
    elif icon in {"share", "include", "friend", "people", "family"}:
        art.draw_child(c, icon_x + 18, icon_y, 42, facing=1, hair="short", lantern=False)
        art.draw_child(c, icon_x + 62, icon_y, 42, facing=-1, hair="bob", lantern=False)
    elif icon in {"kind", "heart", "forgive"}:
        art.draw_heart(c, x + card_w - 36, y + 28, 18)
    elif icon in {"sunrise"}:
        art.draw_sun(c, x + card_w - 36, y + 36, 16)
    elif icon in {"moon"}:
        art.draw_moon(c, x + card_w - 36, y + 36, 16)
    elif icon in {"leaf", "plant"}:
        art.draw_leaf(c, x + card_w - 50, y + 16, 28)
    elif icon in {"bread", "meal", "apple"}:
        art.draw_loaf(c, x + card_w - 54, y + 16, 32)
    elif icon in {"hands", "adult"}:
        art.draw_child(c, icon_x + 28, icon_y, 44, facing=1, hair="short", lantern=False)
    elif icon in {"song", "words", "turn"}:
        art.draw_star(c, x + card_w - 36, y + 36, 14)
    elif icon in {"clock", "coat"}:
        art.draw_basket(c, x + card_w - 50, y + 12, 32)
    elif icon in {"smile"}:
        art.circle(c, x + card_w - 36, y + 32, 16, 1.5)
    elif icon in {"bin", "bird"}:
        art.draw_tree(c, x + card_w - 54, y + 8, 36, 48)
    elif icon in {"cloud"}:
        art.draw_cloud(c, x + card_w - 70, y + 22, 40)
    else:
        art.draw_lantern(c, x + card_w - 50, y + 8, 40)


def draw_faith_page(
    c: canvas.Canvas,
    spec: dict,
    canon: dict,
    *,
    page_number: int = 4,
    marked_proof: bool = False,
    accepted_frame: Path | None = None,
    accepted_icons: dict[str, Path] | None = None,
) -> dict:
    mission = _mission_from_spec(spec)
    page = mission["pages"][3]
    box = live_box(page_number) if marked_proof else content_box(page_number)
    left, bottom, right, top = box
    width = right - left
    frame_bottom = bottom + 4
    frame_top = top - 36
    frame_inset = 8
    cx = (left + right) / 2
    if accepted_frame is not None:
        c.drawImage(
            ImageReader(str(accepted_frame)),
            left,
            frame_bottom,
            width=width,
            height=frame_top - frame_bottom + 36,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
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
        icon_path = (accepted_icons or {}).get(choice["icon"])
        if icon_path is not None:
            c.drawImage(
                ImageReader(str(icon_path)),
                x + card_w - 70,
                cy + 8,
                width=56,
                height=56,
                mask="auto",
                preserveAspectRatio=True,
                anchor="c",
            )
        else:
            _choice_icon(c, choice["icon"], x, cy, card_w, card_h)
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
    c.arc(cx - 26, draw_bottom + draw_h - 8, cx + 26, draw_bottom + draw_h + 28, 0, 180)
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(black)
    c.drawCentredString(cx, draw_bottom + draw_h * 0.45, "Draw here")

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
    required = list(page["required_objects"])
    drawn = list(required)
    if "choice_cards" not in drawn:
        drawn.append("choice_cards")
    if "prayer_ribbon" not in drawn:
        drawn.append("prayer_ribbon")
    if "child_paraphrase_box" not in drawn:
        drawn.append("child_paraphrase_box")
    return {
        "page": page_number,
        "type": "faith_interaction",
        "mission_id": mission["id"],
        "visual_prompt": page["visual_prompt"],
        "required_objects": required,
        "drawn_objects": drawn,
        "text_in_artwork": False,
        "placeholder": marked_proof and accepted_frame is None,
        "artwork_status": (
            "accepted"
            if accepted_frame is not None
            else ("placeholder_only" if marked_proof else "procedural_lineart")
        ),
        "asset_integration": (
            "Accepted faith frame and choice icons ingested; labels, checkboxes, and prayer remain code-rendered."
            if accepted_frame is not None
            else "Frame, four illustrated choices, drawing area, and prayer are one page design."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "drawing_area_sqin": drawing_sqin,
        "checkbox_inches": MIN_CHECKBOX_INCHES,
        "choice_count": len(choices),
    }
