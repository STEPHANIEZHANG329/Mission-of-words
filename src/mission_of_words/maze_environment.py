"""Render a deterministic maze as part of an illustrated environment.

The maze graph stays the generator (unique solvable path). Walls are drawn as
hedges, orchard rows, booths, creek banks, etc. There is no white window.
"""

from __future__ import annotations

from reportlab.lib.colors import Color, white
from reportlab.pdfgen import canvas

from mission_of_words.maze import Maze
from mission_of_words.typefaces import BODY_BOLD, register

INK = Color(0.08, 0.08, 0.08)
PATH = Color(0.93, 0.93, 0.90)
HEDGE = Color(0.18, 0.18, 0.18)
GROUND = Color(0.86, 0.86, 0.82)


def environment_origin(
    box: tuple[float, float, float, float],
    maze: Maze,
    *,
    start_gutter: float = 54,
    finish_gutter: float = 54,
) -> tuple[float, float, float]:
    left, bottom, right, top = box
    inner_w = right - left - start_gutter - finish_gutter
    inner_h = top - bottom - 18
    cell = min(inner_w / maze.cols, inner_h / maze.rows)
    maze_w = cell * maze.cols
    maze_h = cell * maze.rows
    x0 = left + start_gutter + (inner_w - maze_w) / 2
    y0 = bottom + (top - bottom - maze_h) / 2
    return x0, y0, cell


def cell_center(x0: float, y0: float, cell: float, row: int, col: int) -> tuple[float, float]:
    return x0 + (col + 0.5) * cell, y0 + (row + 0.5) * cell


def _linked(maze: Maze, cell: tuple[int, int], other: tuple[int, int]) -> bool:
    return other in maze.passages[cell]


def draw_environment_maze(
    c: canvas.Canvas,
    maze: Maze,
    box: tuple[float, float, float, float],
    *,
    environment_kind: str,
    answer_key: bool = False,
) -> dict:
    register()
    x0, y0, cell = environment_origin(box, maze)
    left, bottom, right, top = box
    c.setFillColor(GROUND)
    c.rect(left, bottom, right - left, top - bottom, fill=1, stroke=0)

    for r in range(maze.rows):
        for col in range(maze.cols):
            x, y = x0 + col * cell, y0 + r * cell
            c.setFillColor(PATH)
            c.rect(x + cell * 0.08, y + cell * 0.08, cell * 0.84, cell * 0.84, fill=1, stroke=0)

    wall = max(2.4, cell * 0.18)
    c.setStrokeColor(INK)
    c.setFillColor(HEDGE)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setLineWidth(wall)

    for r in range(maze.rows):
        for col in range(maze.cols):
            x, y = x0 + col * cell, y0 + r * cell
            cell_id = (r, col)
            start_open = cell_id == maze.start
            finish_open = cell_id == maze.finish
            if not _linked(maze, cell_id, (r + 1, col)) and not finish_open:
                _wall(c, environment_kind, x, y + cell, x + cell, y + cell, cell, "h")
            if not _linked(maze, cell_id, (r - 1, col)):
                _wall(c, environment_kind, x, y, x + cell, y, cell, "h")
            if not _linked(maze, cell_id, (r, col - 1)) and not start_open:
                _wall(c, environment_kind, x, y, x, y + cell, cell, "v")
            if not _linked(maze, cell_id, (r, col + 1)):
                _wall(c, environment_kind, x + cell, y, x + cell, y + cell, cell, "v")

    path = maze.solve() if answer_key else []
    if answer_key:
        c.setStrokeColor(INK)
        c.setLineWidth(max(3.2, cell * 0.28))
        points = [cell_center(x0, y0, cell, r, col) for r, col in path]
        for a, b in zip(points, points[1:]):
            c.line(a[0], a[1], b[0], b[1])

    start = cell_center(x0, y0, cell, maze.start[0], maze.start[1])
    finish = cell_center(x0, y0, cell, maze.finish[0], maze.finish[1])
    return {
        "cell": cell,
        "origin": [x0, y0],
        "path": [list(item) for item in path],
        "start_xy": list(start),
        "finish_xy": list(finish),
        "environment_kind": environment_kind,
        "white_window": False,
    }


def _wall(
    c: canvas.Canvas,
    kind: str,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    cell: float,
    axis: str,
) -> None:
    c.setStrokeColor(INK)
    if kind == "hedge_garden":
        c.setLineWidth(max(3.0, cell * 0.22))
        c.line(x0, y0, x1, y1)
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
        bump = cell * 0.12
        if axis == "h":
            c.circle(mid_x, mid_y + bump, cell * 0.08, fill=0, stroke=1)
        else:
            c.circle(mid_x + bump, mid_y, cell * 0.08, fill=0, stroke=1)
    elif kind == "orchard_rows":
        c.setLineWidth(max(2.6, cell * 0.16))
        c.line(x0, y0, x1, y1)
        if axis == "v":
            c.circle((x0 + x1) / 2, (y0 + y1) / 2 + cell * 0.12, cell * 0.10, fill=0, stroke=1)
    elif kind == "corn_rows":
        c.setLineWidth(max(1.8, cell * 0.10))
        if axis == "v":
            for offset in (-0.12, 0, 0.12):
                c.line(x0 + offset * cell, y0, x1 + offset * cell, y1)
        else:
            c.line(x0, y0, x1, y1)
    elif kind == "woods_trail":
        c.setLineWidth(max(3.4, cell * 0.24))
        c.line(x0, y0, x1, y1)
    elif kind == "garden_path":
        c.setLineWidth(max(2.8, cell * 0.18))
        c.setDash(3, 2)
        c.line(x0, y0, x1, y1)
        c.setDash()
    elif kind == "booth_aisles":
        c.setLineWidth(max(3.6, cell * 0.26))
        c.rect(min(x0, x1) - 1, min(y0, y1) - 1, abs(x1 - x0) + 2, abs(y1 - y0) + 2, fill=0, stroke=1)
    elif kind == "creek_bank":
        c.setLineWidth(max(2.4, cell * 0.16))
        c.setDash(1, 2)
        c.line(x0, y0, x1, y1)
        c.setDash()
    elif kind == "table_path":
        c.setLineWidth(max(2.2, cell * 0.14))
        c.roundRect(min(x0, x1) - 2, min(y0, y1) - 2, abs(x1 - x0) + 4, abs(y1 - y0) + 4, 3, fill=0, stroke=1)
    else:
        c.setLineWidth(max(2.8, cell * 0.18))
        c.line(x0, y0, x1, y1)


def draw_slot_label(
    c: canvas.Canvas,
    x: float,
    y: float,
    label: str,
    *,
    align: str = "left",
) -> None:
    register()
    c.setFillColor(INK)
    c.setFont(BODY_BOLD, 12)
    if align == "right":
        c.drawRightString(x, y, label)
    else:
        c.drawString(x, y, label)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.setFillColor(white)
    c.circle(x + (8 if align == "left" else -8), y + 18, 10, fill=1, stroke=1)
