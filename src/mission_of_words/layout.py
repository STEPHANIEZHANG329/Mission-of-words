"""KDP geometry and typography floors for the 4-page prototype."""

from __future__ import annotations

from reportlab.lib.units import inch

TRIM_INCHES = (8.5, 11.0)
DPI = 300
SAFE_MARGIN_INCHES = 0.50
MIN_INSTRUCTION_PT = 12
MIN_PUZZLE_LETTER_PT = 12
MIN_ANSWER_KEY_PT = 9

PAGE_W = TRIM_INCHES[0] * inch
PAGE_H = TRIM_INCHES[1] * inch
MARGIN = SAFE_MARGIN_INCHES * inch

# Font sizes actually used by the deterministic builder. QA compares these
# against the floors above; they must never be lowered without a QA failure.
USED_INSTRUCTION_PT = 12
USED_PUZZLE_LETTER_PT = 12
USED_ANSWER_KEY_PT = 9
USED_TITLE_PT = 20


def layout_metrics() -> dict:
    return {
        "trim_inches": list(TRIM_INCHES),
        "dpi": DPI,
        "safe_margin_inches": SAFE_MARGIN_INCHES,
        "min_instruction_pt": MIN_INSTRUCTION_PT,
        "min_puzzle_letter_pt": MIN_PUZZLE_LETTER_PT,
        "min_answer_key_pt": MIN_ANSWER_KEY_PT,
        "used_instruction_pt": USED_INSTRUCTION_PT,
        "used_puzzle_letter_pt": USED_PUZZLE_LETTER_PT,
        "used_answer_key_pt": USED_ANSWER_KEY_PT,
    }
