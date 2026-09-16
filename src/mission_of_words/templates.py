"""Reusable Bright Hearts page templates.

Models draw; code decides. All titles, badges, verses, instructions, and
page numbers are measured, wrapped, and collision-checked before ink.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import black, white, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.geometry import (
    BBox,
    LayoutState,
    line_bbox,
    measuring_canvas,
    new_state,
    wrap_lines,
)
from mission_of_words.fonts import FONT_BODY, FONT_BODY_BOLD, FONT_ITALIC, FONT_TITLE, FONT_TITLE_BOLD
from mission_of_words.layout import (
    DPI,
    PAGE_H,
    USED_ANSWER_KEY_PT,
    USED_INSTRUCTION_LEADING,
    USED_INSTRUCTION_PT,
    USED_PUZZLE_LETTER_PT,
    USED_TITLE_PT,
    content_box,
)
from mission_of_words.text import ink_text

BADGE_PT = 9
BADGE_LEADING = 11
ACTIVITY_TITLE_PT = 16
REFERENCE_PT = 11
HERO_INSTRUCTION_PT = 14
HERO_INSTRUCTION_LEADING = 18
HEADER_GAP = 6
ART_GAP = 10
FOOTER_PT = 10
MIN_TITLE_PT = 20
INK = Color(0.07, 0.07, 0.07)


@dataclass
class HeaderPlan:
    state: LayoutState
    art_box: tuple[float, float, float, float]
    footer_box: BBox
    y_below: float


def _content(page_number: int, box: tuple[float, float, float, float] | None) -> tuple[float, float, float, float]:
    return box or content_box(page_number)


def draw_badge(
    c: canvas.Canvas,
    state: LayoutState,
    *,
    x: float,
    y_top: float,
    number: int,
    draw: bool,
    activity_label: str = "",
) -> BBox:
    """Compact mission identifier. A small kicker line, not a competing chip."""
    label = f"MISSION {int(number)}"
    if activity_label:
        label = f"{label}  ·  {activity_label.upper()}"
    font, size = FONT_TITLE_BOLD, BADGE_PT
    text_w = c.stringWidth(label, font, size)
    height = size + 4
    box = BBox("mission_badge", x, y_top - height, x + text_w, y_top, kind="badge")
    state.add(box)
    if draw:
        ink_text(c)
        c.setFillColor(INK)
        c.setFont(font, size)
        c.drawString(x, y_top - size, label)
    return box


def _draw_wrapped(
    c: canvas.Canvas,
    state: LayoutState,
    *,
    name: str,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font: str,
    size: float,
    leading: float,
    draw: bool,
    kind: str = "text",
) -> float:
    lines, overflow = wrap_lines(c, text, font, size, max_width)
    state.overflow.extend(f"{name}: {item}" if not item.startswith(name) else item for item in overflow)
    if draw:
        ink_text(c)
        c.setFillColor(INK)
        c.setFont(font, size)
    for index, line in enumerate(lines):
        baseline = y - index * leading
        box = line_bbox(f"{name}:{index}", x, baseline, line, font, size, c, kind=kind)
        # Extend each line box to the column width only for collision against
        # sibling header bands, not the full column — use the inked width so
        # a short kicker cannot collide with a wrapped title beside it.
        state.add(box)
        if draw:
            c.drawString(x, baseline, line)
    return y - max(len(lines), 1) * leading


def plan_activity_header(
    c: canvas.Canvas,
    page_number: int,
    *,
    mission_number: int | None = None,
    mission_title: str = "",
    activity_title: str = "",
    reference: str = "",
    activity_label: str = "",
    instruction: str = "",
    hero: bool = False,
    box: tuple[float, float, float, float] | None = None,
    draw: bool = True,
) -> HeaderPlan:
    """Compact kicker + wrapping title + verse. Child prompt sits under the scene."""
    left, bottom, right, top = _content(page_number, box)
    width = right - left
    state = new_state(page_number, (left, bottom, right, top))
    title_pt = USED_TITLE_PT if not hero else max(USED_TITLE_PT, 22)
    title_lead = title_pt + 4
    instr_pt = HERO_INSTRUCTION_PT if hero else USED_INSTRUCTION_PT
    instr_lead = HERO_INSTRUCTION_LEADING if hero else USED_INSTRUCTION_LEADING

    footer_h = FOOTER_PT + 6
    prompt_width = width - 42
    prompt_lines, prompt_overflow = wrap_lines(c, instruction, FONT_BODY, instr_pt, prompt_width) if instruction else ([], [])
    state.overflow.extend(prompt_overflow)
    prompt_h = max(len(prompt_lines), 1) * instr_lead + 8 if instruction else 0
    art_bottom = bottom + footer_h + prompt_h + 4

    footer = BBox("page_number", right - 36, bottom, right, bottom + footer_h, kind="folio")
    state.add(footer)
    if draw:
        ink_text(c)
        c.setFillColor(INK)
        c.setFont(FONT_BODY, FOOTER_PT)
        c.drawRightString(right, bottom + 2, str(page_number))

    if instruction:
        y_prompt = bottom + footer_h + (len(prompt_lines) - 1) * instr_lead + 4
        for index, line in enumerate(prompt_lines):
            baseline = y_prompt - index * instr_lead
            box_line = line_bbox(f"instruction:{index}", left, baseline, line, FONT_BODY, instr_pt, c)
            state.add(box_line)
            if draw:
                ink_text(c)
                c.setFillColor(INK)
                c.setFont(FONT_BODY, instr_pt)
                c.drawString(left, baseline, line)

    y = top - 2
    if mission_number is not None:
        badge = draw_badge(
            c,
            state,
            x=left,
            y_top=y,
            number=mission_number,
            draw=draw,
            activity_label=activity_label,
        )
        y = badge.y0 - HEADER_GAP - title_pt * 0.78
    else:
        y = top - title_pt * 0.88 - 4
    display_title = mission_title or activity_title
    if display_title:
        y = _draw_wrapped(
            c,
            state,
            name="mission_title",
            text=display_title,
            x=left,
            y=y,
            max_width=width,
            font=FONT_TITLE_BOLD,
            size=title_pt,
            leading=title_lead,
            draw=draw,
        )
    if reference:
        y -= 4
        y = _draw_wrapped(
            c,
            state,
            name="kicker",
            text=reference,
            x=left,
            y=y,
            max_width=width,
            font=FONT_ITALIC,
            size=REFERENCE_PT,
            leading=REFERENCE_PT + 3,
            draw=draw,
        )

    y_below = y - ART_GAP
    if y_below - art_bottom < 160:
        state.overflow.append("header consumed the art area")
    art_box = (left, art_bottom, right, y_below)
    return HeaderPlan(state=state, art_box=art_box, footer_box=footer, y_below=y_below)


def draw_activity_header(
    c: canvas.Canvas,
    page_number: int,
    **kwargs,
) -> HeaderPlan:
    return plan_activity_header(c, page_number, draw=True, **kwargs)


def measure_activity_header(page_number: int, **kwargs) -> HeaderPlan:
    return plan_activity_header(measuring_canvas(), page_number, draw=False, **kwargs)


def draw_panel(c: canvas.Canvas, box: tuple[float, float, float, float], *, radius: float = 14, width: float = 2.0) -> None:
    left, bottom, right, top = box
    art.ink(c, width)
    c.roundRect(left, bottom, right - left, top - bottom, radius, fill=1, stroke=1)


def place_raster(
    c: canvas.Canvas,
    path: Path,
    box: tuple[float, float, float, float],
    state: LayoutState,
    *,
    name: str = "raster",
    preserve: bool = True,
) -> dict:
    left, bottom, right, top = box
    frame_w = right - left
    frame_h = top - bottom
    with Image.open(path) as image:
        img_w, img_h = image.size
    if preserve:
        fill = min(frame_w / img_w, frame_h / img_h)
        native_300 = 72.0 / DPI
        scale = min(fill, native_300)
        draw_w, draw_h = img_w * scale, img_h * scale
        x = left + (frame_w - draw_w) / 2
        y = bottom + (frame_h - draw_h) / 2
    else:
        draw_w, draw_h = frame_w, frame_h
        x, y = left, bottom
    c.drawImage(
        ImageReader(str(path)),
        x,
        y,
        width=draw_w,
        height=draw_h,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    placed = BBox(name, x, y, x + draw_w, y + draw_h, kind="raster")
    state.add(placed)
    width_in = draw_w / 72.0
    height_in = draw_h / 72.0
    effective = min(img_w / width_in, img_h / height_in) if width_in and height_in else 0.0
    return {
        "raster_pixel_size": [img_w, img_h],
        "placed_points": [draw_w, draw_h],
        "placed_box": [x, y, x + draw_w, y + draw_h],
        "effective_dpi": effective,
        "source_dpi_ok": effective + 0.05 >= DPI,
        "upsampled": img_w < draw_w * DPI / 72.0 - 0.5 or img_h < draw_h * DPI / 72.0 - 0.5,
    }


def draw_maze_grid(
    c: canvas.Canvas,
    maze,
    *,
    x0: float,
    y0: float,
    cell: float,
    answer_key: bool = False,
    solution_weight: float | None = None,
) -> dict:
    wall = max(2.2, cell * 0.16)
    c.setStrokeColor(INK)
    c.setFillColor(white)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setLineWidth(wall)

    def cell_xy(row: int, col: int) -> tuple[float, float]:
        return x0 + col * cell, y0 + row * cell

    for r in range(maze.rows):
        for col in range(maze.cols):
            x, y_cell = cell_xy(r, col)
            linked = maze.passages[(r, col)]
            start_open = (r, col) == maze.start
            finish_open = (r, col) == maze.finish
            if (r + 1, col) not in linked and not finish_open:
                c.line(x, y_cell + cell, x + cell, y_cell + cell)
            if (r - 1, col) not in linked:
                c.line(x, y_cell, x + cell, y_cell)
            if (r, col - 1) not in linked and not start_open:
                c.line(x, y_cell, x, y_cell + cell)
            if (r, col + 1) not in linked:
                c.line(x + cell, y_cell, x + cell, y_cell + cell)

    path = maze.solve() if answer_key else []
    if answer_key:
        c.setStrokeColor(INK)
        c.setLineWidth(solution_weight or max(3.0, cell * 0.28))
        points = [(x0 + (col + 0.5) * cell, y0 + (r + 0.5) * cell) for r, col in path]
        for a, b in zip(points, points[1:]):
            c.line(a[0], a[1], b[0], b[1])
    return {"cell": cell, "origin": [x0, y0], "path": [list(item) for item in path]}


def maze_window_box(art_box: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    left, bottom, right, top = art_box
    width, height = right - left, top - bottom
    pad_x, pad_y = width * 0.06, height * 0.08
    return left + pad_x, bottom + pad_y, right - pad_x, top - pad_y


def draw_start_finish_badges(
    c: canvas.Canvas,
    state: LayoutState,
    *,
    start_xy: tuple[float, float],
    finish_xy: tuple[float, float],
    start_label: str,
    finish_label: str,
    cell: float,
) -> None:
    font, size = FONT_TITLE_BOLD, USED_PUZZLE_LETTER_PT
    for name, label, (x, y) in (
        ("start_label", start_label, start_xy),
        ("finish_label", finish_label, finish_xy),
    ):
        text_w = c.stringWidth(label, font, size)
        bx = x - text_w / 2
        by = y - size * 0.2
        box = BBox(name, bx - 6, by - 4, bx + text_w + 6, by + size + 4, kind="label")
        state.add(box)
        art.ink(c, 1.6)
        c.roundRect(box.x0, box.y0, box.width(), box.height(), 6, fill=1, stroke=1)
        ink_text(c)
        c.setFillColor(INK)
        c.setFont(font, size)
        c.drawString(bx, by, label)


def effective_dpi(pixel_size: tuple[int, int], placed_points: tuple[float, float]) -> float:
    img_w, img_h = pixel_size
    placed_w, placed_h = placed_points
    width_in = placed_w / 72.0
    height_in = placed_h / 72.0
    if not width_in or not height_in:
        return 0.0
    return min(img_w / width_in, img_h / height_in)


def draw_answer_number(
    c: canvas.Canvas,
    cx: float,
    cy: float,
    radius: float,
    number: int,
    state: LayoutState | None = None,
    name: str = "callout",
    *,
    track: bool = False,
) -> None:
    c.setStrokeColor(INK)
    c.setLineWidth(1.8)
    c.setFillColor(white)
    c.circle(cx, cy, radius, fill=0, stroke=1)
    label = str(number)
    font, size = FONT_BODY_BOLD, max(USED_ANSWER_KEY_PT, 11)
    text_w = c.stringWidth(label, font, size)
    lx = cx - text_w / 2
    ly = cy + radius + 3
    if track and state is not None:
        box = BBox(
            name,
            min(cx - radius, lx),
            min(cy - radius, ly - 2),
            max(cx + radius, lx + text_w),
            ly + size,
            kind="callout",
        )
        state.add(box)
    ink_text(c)
    c.setFont(font, size)
    c.drawString(lx, ly, label)
