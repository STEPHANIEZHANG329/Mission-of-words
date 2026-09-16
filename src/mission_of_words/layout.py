"""KDP geometry and typography floors for the 4-page prototype."""

from __future__ import annotations

from reportlab.lib.units import inch

TRIM_INCHES = (8.5, 11.0)
DPI = 300
SAFE_MARGIN_INCHES = 0.50
# Inside/gutter is strictly greater than the outer safety so facing-page
# parity is real, not a comment. Both remain >= 0.50 in.
INNER_SAFETY_INCHES = 0.625
OUTER_SAFETY_INCHES = 0.50
TOP_SAFETY_INCHES = 0.50
BOTTOM_SAFETY_INCHES = 0.50
MIN_INSTRUCTION_PT = 12
MIN_PUZZLE_LETTER_PT = 12
MIN_ANSWER_KEY_PT = 9
MIN_FAITH_DRAWING_SQIN = 10.0
MIN_CHECKBOX_INCHES = 0.28

PAGE_W = TRIM_INCHES[0] * inch
PAGE_H = TRIM_INCHES[1] * inch
MARGIN = SAFE_MARGIN_INCHES * inch

# Font sizes actually used by the deterministic builder. QA compares these
# against the floors above; they must never be lowered without a QA failure.
USED_INSTRUCTION_PT = 13
USED_INSTRUCTION_LEADING = 17
USED_PUZZLE_LETTER_PT = 12
USED_ANSWER_KEY_PT = 9
USED_TITLE_PT = 24
USED_SUBTITLE_PT = 12
USED_ACTIVITY_TITLE_PT = 16
USED_HERO_INSTRUCTION_PT = 14
USED_BADGE_PT = 10


def page_margins_inches(page_number: int) -> dict[str, float]:
    """1-based page index. Odd pages are recto (right-hand); inner is left."""
    if page_number < 1:
        raise ValueError(f"page_number must be >= 1, got {page_number}")
    inner = INNER_SAFETY_INCHES
    outer = OUTER_SAFETY_INCHES
    if page_number % 2 == 1:
        left, right = inner, outer
    else:
        left, right = outer, inner
    return {
        "left": left,
        "right": right,
        "top": TOP_SAFETY_INCHES,
        "bottom": BOTTOM_SAFETY_INCHES,
        "inner": inner,
        "outer": outer,
    }


def content_box(page_number: int) -> tuple[float, float, float, float]:
    """Return (left, bottom, right, top) in points for the live safety box."""
    margins = page_margins_inches(page_number)
    left = margins["left"] * inch
    bottom = margins["bottom"] * inch
    right = PAGE_W - margins["right"] * inch
    top = PAGE_H - margins["top"] * inch
    return left, bottom, right, top


def content_size_inches(page_number: int) -> tuple[float, float]:
    left, bottom, right, top = content_box(page_number)
    return (right - left) / inch, (top - bottom) / inch


def layout_metrics() -> dict:
    return {
        "trim_inches": list(TRIM_INCHES),
        "dpi": DPI,
        "safe_margin_inches": SAFE_MARGIN_INCHES,
        "inner_safety_inches": INNER_SAFETY_INCHES,
        "outer_safety_inches": OUTER_SAFETY_INCHES,
        "min_instruction_pt": MIN_INSTRUCTION_PT,
        "min_puzzle_letter_pt": MIN_PUZZLE_LETTER_PT,
        "min_answer_key_pt": MIN_ANSWER_KEY_PT,
        "used_instruction_pt": USED_INSTRUCTION_PT,
        "used_puzzle_letter_pt": USED_PUZZLE_LETTER_PT,
        "used_answer_key_pt": USED_ANSWER_KEY_PT,
        "used_title_pt": USED_TITLE_PT,
        "min_faith_drawing_sqin": MIN_FAITH_DRAWING_SQIN,
        "facing_page_parity": True,
        "no_bleed": True,
    }
