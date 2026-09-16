"""Shared PDF text drawing, always inside a page's facing-page safety box."""

from __future__ import annotations

from reportlab.lib.colors import black
from reportlab.pdfgen import canvas

from mission_of_words.fonts import FONT_BODY
from mission_of_words.layout import (
    USED_INSTRUCTION_LEADING,
    USED_INSTRUCTION_PT,
    content_box,
)


def ink_text(c: canvas.Canvas) -> None:
    """ReportLab uses fill color for glyphs; art.ink() leaves fill white."""
    c.setFillColor(black)
    c.setStrokeColor(black)
    c.setDash()


def wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    *,
    font: str = FONT_BODY,
    size: int = USED_INSTRUCTION_PT,
    leading: float = USED_INSTRUCTION_LEADING,
) -> float:
    ink_text(c)
    c.setFont(font, size)
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            line = trial
            continue
        c.drawString(x, y, line)
        y -= leading
        line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def page_header(
    c: canvas.Canvas,
    page_number: int,
    title: str,
    instruction: str,
    *,
    kicker: str | None = None,
    box: tuple[float, float, float, float] | None = None,
    mission_number: int | None = None,
    mission_title: str = "",
    activity_label: str = "",
    hero: bool = False,
) -> tuple[tuple[float, float, float, float], float, HeaderPlan]:
    """Draw the reusable activity header. Returns (content_box, y_below, plan)."""
    from mission_of_words.templates import draw_activity_header

    reference = ""
    label = activity_label
    if kicker and "·" in kicker:
        reference, _, rest = kicker.partition("·")
        reference = reference.strip()
        extra = rest.strip()
        label = extra or activity_label
    elif kicker:
        reference = kicker
    plan = draw_activity_header(
        c,
        page_number,
        mission_number=mission_number,
        mission_title=mission_title,
        activity_title=title,
        reference=reference,
        activity_label=label,
        instruction=instruction,
        hero=hero,
        box=box,
    )
    left, bottom, right, top = box or content_box(page_number)
    return (left, bottom, right, top), plan.y_below, plan
