"""KDP page geometry. All values in inches unless noted."""

from __future__ import annotations

from dataclasses import dataclass

TRIM_W = 8.5
TRIM_H = 11.0
DPI = 300
INNER_SAFETY = 0.625
OUTER_SAFETY = 0.50
TOP_SAFETY = 0.50
BOTTOM_SAFETY = 0.55
BLEED = 0.125
SPINE_WHITE_PAPER = 0.002252  # inches per page, KDP white paper
MIN_INSTRUCTION_PT = 12.0
MIN_PUZZLE_PT = 12.0
MIN_ANSWER_PT = 9.0
MIN_TITLE_PT = 16.0


@dataclass(frozen=True)
class Margins:
    left: float
    right: float
    top: float
    bottom: float

    @property
    def content_width(self) -> float:
        return TRIM_W - self.left - self.right

    @property
    def content_height(self) -> float:
        return TRIM_H - self.top - self.bottom


def margins_for_page(page_number: int) -> Margins:
    """Odd pages are recto (right-hand): gutter on the left."""
    if page_number < 1:
        raise ValueError("page numbers are 1-based")
    odd = page_number % 2 == 1
    if odd:
        return Margins(left=INNER_SAFETY, right=OUTER_SAFETY, top=TOP_SAFETY, bottom=BOTTOM_SAFETY)
    return Margins(left=OUTER_SAFETY, right=INNER_SAFETY, top=TOP_SAFETY, bottom=BOTTOM_SAFETY)


def pt(inches: float) -> float:
    return inches * 72.0


def px(inches: float, dpi: int = DPI) -> int:
    return int(round(inches * dpi))


def cover_size_inches(page_count: int = 48) -> tuple[float, float]:
    spine = spine_width_inches(page_count)
    width = BLEED + TRIM_W + spine + TRIM_W + BLEED
    height = TRIM_H + BLEED * 2
    return width, height


def spine_width_inches(page_count: int = 48) -> float:
    return SPINE_WHITE_PAPER * page_count
