"""INTERNAL geometry-mock markings. These pages are never product."""

from __future__ import annotations

from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas

from mission_of_words.layout import content_box
from mission_of_words.text import ink_text
from mission_of_words.typefaces import BODY_BOLD, BODY_ITALIC, register

INTERNAL_MOCK_MARK = "INTERNAL GEOMETRY MOCK"
INTERNAL_MOCK_LINE = "INTERNAL GEOMETRY MOCK — NOT PRODUCT — NOT FOR OWNER REVIEW"
NON_PRODUCTION_MARK = INTERNAL_MOCK_MARK
NON_PRODUCTION_LINE = INTERNAL_MOCK_LINE
PROOF_FOOTER_PT = 22.0
FORBIDDEN_PRODUCT_LABELS = (
    "KDP-READY",
    "COMMERCIAL LAYOUT PROOF",
    "PRODUCTION CANDIDATE",
    "PUBLISHABLE",
)
WATERMARK = Color(0.82, 0.18, 0.18)


def live_box(page_number: int) -> tuple[float, float, float, float]:
    left, bottom, right, top = content_box(page_number)
    return left, bottom + PROOF_FOOTER_PT, right, top


def draw_proof_mark(c: canvas.Canvas, page_number: int) -> None:
    register()
    left, bottom, right, _top = content_box(page_number)
    ink_text(c)
    c.setFillColor(WATERMARK)
    c.setFont(BODY_BOLD, 8)
    c.drawCentredString((left + right) / 2, bottom + 8, INTERNAL_MOCK_LINE)
    c.setFont(BODY_ITALIC, 7)
    c.drawCentredString((left + right) / 2, bottom + 1, "Engineering geometry only. Do not send to Owner as product.")


def draw_diagonal_watermark(c: canvas.Canvas) -> None:
    register()
    c.saveState()
    c.setFillColor(Color(0.92, 0.55, 0.55))
    c.setFont(BODY_BOLD, 18)
    c.translate(306, 396)
    c.rotate(38)
    for offset in range(-3, 4):
        c.drawCentredString(0, offset * 90, INTERNAL_MOCK_MARK)
    c.restoreState()
