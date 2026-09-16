"""KDP paperback wrap cover. Interior page count is locked at 48."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words.layout import TRIM_INCHES
from mission_of_words.paths import OUTPUT_DIR
from mission_of_words.text import ink_text, wrapped_text

PAGE_COUNT = 48
BLEED_IN = 0.125
SPINE_IN = PAGE_COUNT * 0.002252  # KDP white B&W
WRAP_W_IN = BLEED_IN + TRIM_INCHES[0] + SPINE_IN + TRIM_INCHES[0] + BLEED_IN
WRAP_H_IN = TRIM_INCHES[1] + 2 * BLEED_IN
SAFE = 0.5 * inch
TITLE = "Bright Hearts"
SUBTITLE = "Shine Your Light This Fall"
TAG = "A Christian Fall Activity Book for Kids Ages 5–8"
BLURB = (
    "Eight Bible-first fall missions for ages 5-8: coloring, Search & Find, mazes, "
    "and Faith in Action pages. Let your light shine. Give thanks. Share. Be kind."
)


def wrap_points() -> tuple[float, float]:
    return WRAP_W_IN * inch, WRAP_H_IN * inch


def front_rect() -> tuple[float, float, float, float]:
    """left, bottom, right, top of the front cover panel including bleed on the outer edges."""
    w, h = wrap_points()
    left = (BLEED_IN + TRIM_INCHES[0] + SPINE_IN) * inch
    return left, 0, w, h


def draw_cover(c: canvas.Canvas, *, artwork: Path | None = None) -> dict:
    w, h = wrap_points()
    c.setFillColor(Color(0.18, 0.22, 0.16))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    # spine
    spine_left = (BLEED_IN + TRIM_INCHES[0]) * inch
    spine_w = SPINE_IN * inch
    c.setFillColor(Color(0.33, 0.22, 0.10))
    c.rect(spine_left, 0, spine_w, h, fill=1, stroke=0)
    fl, fb, fr, ft = front_rect()
    if artwork and Path(artwork).is_file():
        c.drawImage(ImageReader(str(artwork)), fl, fb, width=fr - fl, height=ft - fb, preserveAspectRatio=True, anchor="c")
    else:
        c.setFillColor(Color(0.86, 0.74, 0.48))
        c.rect(fl, fb, fr - fl, ft - fb, fill=1, stroke=0)
    # code-rendered type on the front
    text_left = fl + (BLEED_IN + 0.5) * inch
    text_right = fr - (BLEED_IN + 0.5) * inch
    ink_text(c)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(text_left, ft - 1.1 * inch, TITLE)
    c.setFont("Helvetica-Bold", 16)
    wrapped_text(c, SUBTITLE, text_left, ft - 1.45 * inch, text_right - text_left, font="Helvetica-Bold", size=16, leading=20)
    c.setFont("Helvetica", 12)
    wrapped_text(c, TAG, text_left, ft - 2.05 * inch, text_right - text_left, size=12, leading=16)
    # back blurb
    back_left = BLEED_IN * inch + SAFE
    back_right = spine_left - SAFE
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(back_left, ft - 1.3 * inch, TITLE)
    wrapped_text(c, BLURB, back_left, ft - 1.7 * inch, back_right - back_left, size=12, leading=16)
    c.setFont("Helvetica", 10)
    c.drawString(back_left, fb + 0.7 * inch, "Ages 5–8  ·  Paperback  ·  8.5 × 11 in")
    # spine type
    c.saveState()
    c.translate(spine_left + spine_w / 2, h / 2)
    c.rotate(90)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(0, -3, "Bright Hearts  ·  Shine Your Light This Fall")
    c.restoreState()
    return {
        "trim_inches": list(TRIM_INCHES),
        "page_count": PAGE_COUNT,
        "spine_inches": SPINE_IN,
        "wrap_inches": [WRAP_W_IN, WRAP_H_IN],
        "bleed_inches": BLEED_IN,
        "artwork": str(artwork) if artwork else None,
    }


def write_cover_pdf(path: Path | None = None, artwork: Path | None = None) -> Path:
    dest = path or (OUTPUT_DIR / "BrightHearts_Fall_Cover.pdf")
    dest.parent.mkdir(parents=True, exist_ok=True)
    w, h = wrap_points()
    c = canvas.Canvas(str(dest), pagesize=(w, h))
    meta = draw_cover(c, artwork=artwork)
    c.showPage()
    c.save()
    (OUTPUT_DIR / "cover_geometry.json").write_text(
        __import__("json").dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return dest
