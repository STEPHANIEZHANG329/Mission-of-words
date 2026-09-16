"""Page 3: one illustrated maze. The child, path, and table are one scene."""

from __future__ import annotations

from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.layout import USED_PUZZLE_LETTER_PT
from mission_of_words.maze import Maze
from mission_of_words.text import ink_text, page_header


def draw_maze_page(
    c: canvas.Canvas,
    spec: dict,
    maze: Maze,
    *,
    answer_key: bool = False,
    page_number: int = 3,
) -> dict:
    page = spec["mission"]["pages"][2]
    title = page["title"] if not answer_key else "Maze — Answer Key"
    instruction = (
        page["child_instruction"]
        if not answer_key
        else "The dark line is the one unique path through the hedge."
    )
    box, y = page_header(
        c,
        page_number,
        title,
        instruction,
        kicker="Matthew 5:16  ·  Carry the lantern",
    )
    left, bottom, right, top = box
    width = right - left

    stage_top = y
    stage_bottom = bottom + 6
    stage_h = stage_top - stage_bottom

    maze_left = left + width * 0.18
    maze_right = right - width * 0.18
    maze_bottom = stage_bottom + stage_h * 0.18
    maze_top = stage_bottom + stage_h * 0.66
    cell = min((maze_right - maze_left) / maze.cols, (maze_top - maze_bottom) / maze.rows)
    maze_w = cell * maze.cols
    maze_h = cell * maze.rows
    x0 = left + (width - maze_w) / 2
    y0 = maze_bottom

    # Thin ground line under the hedge — no leftover empty box.
    art.ink(c, 1.6)
    c.line(left + 8, y0 - 6, right - 8, y0 - 6)
    art.draw_cloud(c, left + width * 0.06, stage_bottom + stage_h * 0.88, width * 0.16)
    art.draw_cloud(c, left + width * 0.78, stage_bottom + stage_h * 0.90, width * 0.14)
    art.draw_church(c, left + width * 0.36, stage_bottom + stage_h * 0.72, width * 0.26, stage_h * 0.26)
    art.draw_tree(c, left + width * 0.04, stage_bottom + stage_h * 0.50, width * 0.14, stage_h * 0.26)
    art.draw_string_lights(
        c,
        left + width * 0.16,
        stage_bottom + stage_h * 0.78,
        left + width * 0.40,
        stage_bottom + stage_h * 0.88,
        bulbs=5,
    )

    wall = max(2.0, cell * 0.15)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(1, 1, 1)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setLineWidth(wall)

    def cell_xy(row: int, col: int) -> tuple[float, float]:
        # Row 0 at the bottom so the child walks up toward the church table.
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

    start_x, start_y = cell_xy(*maze.start)
    art.draw_child(
        c,
        start_x - cell * 1.35,
        start_y - cell * 0.2,
        cell * 2.4,
        facing=1,
        hair="bob",
        lantern=True,
    )
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_PUZZLE_LETTER_PT)
    c.drawCentredString(start_x - cell * 1.35, start_y - cell * 0.55, page["start_label"])

    fin_x, fin_y = cell_xy(*maze.finish)
    art.draw_table(c, fin_x - cell * 0.4, fin_y + cell * 1.05, cell * 2.6, cell * 1.5)
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_PUZZLE_LETTER_PT)
    c.drawCentredString(fin_x + cell * 0.9, fin_y + cell * 2.7, page["finish_label"])

    if answer_key:
        path = maze.solve()
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(max(2.2, cell * 0.20))
        points = []
        for r, col in path:
            px = x0 + (col + 0.5) * cell
            py = y0 + (r + 0.5) * cell
            points.append((px, py))
        for a, b in zip(points, points[1:]):
            c.line(a[0], a[1], b[0], b[1])

    return {
        "page": 3,
        "type": "maze",
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": [
            "church",
            "child_with_lantern",
            "hedge_maze",
            "welcome_table",
            "start_label",
            "finish_label",
        ],
        "text_in_artwork": False,
        "asset_integration": (
            "The child, hedge, and welcome table share one garden. Start is the "
            "child at the opening; finish is the table under the church."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "start": list(maze.start),
        "finish": list(maze.finish),
        "drawing_area_sqin": None,
    }
