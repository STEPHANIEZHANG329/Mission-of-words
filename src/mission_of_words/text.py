"""Shared PDF text drawing, always inside a page's facing-page safety box."""

from __future__ import annotations

from reportlab.lib.colors import black
from reportlab.pdfgen import canvas

from mission_of_words.layout import (
    USED_INSTRUCTION_LEADING,
    USED_INSTRUCTION_PT,
    USED_SUBTITLE_PT,
    USED_TITLE_PT,
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
    font: str = "Helvetica",
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
) -> tuple[tuple[float, float, float, float], float]:
    """Draw title + child instruction. Returns (content_box, y_below_header)."""
    left, bottom, right, top = content_box(page_number)
    width = right - left
    y = top - 8
    ink_text(c)
    if kicker:
        c.setFont("Helvetica", USED_SUBTITLE_PT)
        c.drawString(left, y - 4, kicker)
        y -= 20
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawString(left, y - 18, title)
    y -= 42
    y = wrapped_text(
        c,
        instruction,
        left,
        y,
        width,
        font="Helvetica",
        size=USED_INSTRUCTION_PT,
        leading=USED_INSTRUCTION_LEADING,
    )
    return (left, bottom, right, top), y - 8
