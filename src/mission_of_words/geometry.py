"""Measured boxes, wrapping, overflow, and collision detection.

All final type is planned in print space before it is drawn. Adjacent
boxes may touch; interiors may not overlap. Boxes must stay inside the
facing-page safety rectangle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from typing import Iterable

from reportlab.pdfgen import canvas as pdfcanvas

from mission_of_words.layout import PAGE_H, PAGE_W, content_box

TOUCH_EPS = 0.51  # points; interiors may not overlap


@dataclass(frozen=True)
class BBox:
    name: str
    x0: float
    y0: float
    x1: float
    y1: float
    kind: str = "text"

    def width(self) -> float:
        return self.x1 - self.x0

    def height(self) -> float:
        return self.y1 - self.y0

    def as_tuple(self) -> tuple[float, float, float, float]:
        return self.x0, self.y0, self.x1, self.y1

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "x0": round(self.x0, 3),
            "y0": round(self.y0, 3),
            "x1": round(self.x1, 3),
            "y1": round(self.y1, 3),
            "kind": self.kind,
        }


def boxes_overlap(a: BBox, b: BBox, gap: float = TOUCH_EPS) -> bool:
    return not (
        a.x1 + gap <= b.x0
        or b.x1 + gap <= a.x0
        or a.y1 + gap <= b.y0
        or b.y1 + gap <= a.y0
    )


def box_clipped(box: BBox, safety: BBox, slop: float = 0.25) -> bool:
    return (
        box.x0 < safety.x0 - slop
        or box.y0 < safety.y0 - slop
        or box.x1 > safety.x1 + slop
        or box.y1 > safety.y1 + slop
    )


def measuring_canvas() -> pdfcanvas.Canvas:
    return pdfcanvas.Canvas(BytesIO(), pagesize=(PAGE_W, PAGE_H))


def wrap_lines(
    c: pdfcanvas.Canvas,
    text: str,
    font: str,
    size: float,
    max_width: float,
) -> tuple[list[str], list[str]]:
    """Word-wrap `text`. Returns (lines, overflow_messages)."""
    overflow: list[str] = []
    words = [part for part in text.replace("\n", " ").split(" ") if part != ""]
    if not words:
        return [""], overflow
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
            current = word
        else:
            current = word
        if c.stringWidth(current, font, size) > max_width:
            overflow.append(
                f"text overflow: {word!r} is {c.stringWidth(current, font, size):.1f}pt "
                f"in a {max_width:.1f}pt column at {size}pt {font}"
            )
    if current:
        lines.append(current)
    return lines, overflow


def line_bbox(
    name: str,
    x: float,
    baseline: float,
    text: str,
    font: str,
    size: float,
    c: pdfcanvas.Canvas,
    *,
    kind: str = "text",
    extra_w: float = 0.0,
) -> BBox:
    width = c.stringWidth(text, font, size) + extra_w
    # Use a conservative em-box so descenders/caps cannot collide.
    return BBox(name, x, baseline - size * 0.22, x + width, baseline + size * 0.82, kind)


@dataclass
class LayoutState:
    page_number: int
    safety: BBox
    bboxes: list[BBox] = field(default_factory=list)
    overflow: list[str] = field(default_factory=list)
    clipped: list[str] = field(default_factory=list)

    def add(self, box: BBox) -> BBox:
        self.bboxes.append(box)
        if box_clipped(box, self.safety):
            self.clipped.append(f"{box.name} clips the {self.safety.name} safety box")
        return box

    def collision_messages(self) -> list[str]:
        skip = {"region", "art", "watermark", "scene", "safety"}
        messages: list[str] = []
        for index, left in enumerate(self.bboxes):
            if left.kind in skip:
                continue
            for right in self.bboxes[index + 1 :]:
                if right.kind in skip:
                    continue
                if boxes_overlap(left, right):
                    messages.append(f"{left.name} overlaps {right.name}")
        return messages

    def ok(self) -> bool:
        return not (self.collision_messages() or self.overflow or self.clipped)

    def as_fields(self) -> dict:
        return {
            "bboxes": [box.as_dict() for box in self.bboxes],
            "collisions": self.collision_messages(),
            "overflow": list(self.overflow),
            "clipped": list(self.clipped),
            "layout_ok": self.ok(),
        }


def safety_bbox(page_number: int, box: tuple[float, float, float, float] | None = None) -> BBox:
    left, bottom, right, top = box or content_box(page_number)
    return BBox("safety", left, bottom, right, top, kind="safety")


def new_state(
    page_number: int, box: tuple[float, float, float, float] | None = None
) -> LayoutState:
    return LayoutState(page_number=page_number, safety=safety_bbox(page_number, box))


def audit_boxes(boxes: Iterable[BBox], safety: BBox) -> dict:
    state = LayoutState(page_number=0, safety=safety, bboxes=list(boxes))
    for box in state.bboxes:
        if box_clipped(box, safety):
            state.clipped.append(f"{box.name} clips the safety box")
    return state.as_fields()
