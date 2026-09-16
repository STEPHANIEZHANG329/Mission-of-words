"""NON-PRODUCTION technical-proof markings.

Placeholder art may never satisfy production readiness. Every composed
technical-proof page carries a visible mark that QA can audit.
"""

from __future__ import annotations

from reportlab.pdfgen import canvas

from mission_of_words.layout import USED_ANSWER_KEY_PT, content_box
from mission_of_words.text import ink_text

NON_PRODUCTION_MARK = "NON-PRODUCTION TECHNICAL PROOF"
NON_PRODUCTION_LINE = "NON-PRODUCTION TECHNICAL PROOF — placeholder art — not for KDP"
PROOF_FOOTER_PT = 16.0
INTERNAL_MARK = "INTERNAL ENGINEERING GEOMETRY"
INTERNAL_LINE = "INTERNAL ENGINEERING GEOMETRY — NOT A PRODUCT — not for KDP"


def draw_internal_stamp(c: canvas.Canvas, page_number: int) -> None:
    """Engineering overlay only. Helvetica is allowed on this stamp, not on consumer type."""
    left, bottom, right, _top = content_box(page_number)
    ink_text(c)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString((left + right) / 2, bottom - 11, INTERNAL_LINE)
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(right, bottom - 11, str(page_number))


def live_box(page_number: int) -> tuple[float, float, float, float]:
    """Content box minus the proof-mark footer strip."""
    left, bottom, right, top = content_box(page_number)
    return left, bottom + PROOF_FOOTER_PT, right, top


def draw_proof_mark(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, _top = content_box(page_number)
    ink_text(c)
    c.setFont("Helvetica-Oblique", USED_ANSWER_KEY_PT)
    c.drawCentredString((left + right) / 2, bottom + 3, NON_PRODUCTION_LINE)
    c.setFont("Helvetica", USED_ANSWER_KEY_PT)
    c.drawRightString(right, bottom + 3 + USED_ANSWER_KEY_PT + 2, f"{page_number}")
