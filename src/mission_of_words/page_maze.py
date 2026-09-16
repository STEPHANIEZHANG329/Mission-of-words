"""Illustrated maze pages. The child, path, and finish share one scene."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.layout import USED_PUZZLE_LETTER_PT
from mission_of_words.maze import Maze
from mission_of_words.proof import live_box
from mission_of_words.text import ink_text, page_header


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def _scenery(c: canvas.Canvas, mission_id: str, left: float, right: float, stage_bottom: float, stage_h: float, width: float) -> None:
    if mission_id == "mission_02":
        art.draw_sun(c, left + width * 0.12, stage_bottom + stage_h * 0.88, width * 0.05)
        art.draw_moon(c, left + width * 0.86, stage_bottom + stage_h * 0.88, width * 0.045)
        art.draw_tree(c, left + width * 0.02, stage_bottom + stage_h * 0.48, width * 0.14, stage_h * 0.28)
        art.draw_tree(c, left + width * 0.84, stage_bottom + stage_h * 0.50, width * 0.12, stage_h * 0.24)
    elif mission_id == "mission_03":
        art.draw_barn(c, left + width * 0.36, stage_bottom + stage_h * 0.70, width * 0.28, stage_h * 0.28)
        art.draw_wheat(c, left + width * 0.08, stage_bottom + stage_h * 0.52, stage_h * 0.18)
        art.draw_cloud(c, left + width * 0.78, stage_bottom + stage_h * 0.88, width * 0.14)
    elif mission_id == "mission_04":
        art.draw_tree(c, left + width * 0.02, stage_bottom + stage_h * 0.48, width * 0.14, stage_h * 0.30)
        art.draw_tree(c, left + width * 0.84, stage_bottom + stage_h * 0.50, width * 0.12, stage_h * 0.26)
        art.draw_porch(c, left + width * 0.36, stage_bottom + stage_h * 0.70, width * 0.28, stage_h * 0.26, lit=True)
    elif mission_id == "mission_05":
        art.draw_porch(c, left + width * 0.36, stage_bottom + stage_h * 0.70, width * 0.28, stage_h * 0.26, lit=False)
        art.draw_cloud(c, left + width * 0.08, stage_bottom + stage_h * 0.88, width * 0.14)
    elif mission_id == "mission_06":
        art.draw_booth(c, left + width * 0.34, stage_bottom + stage_h * 0.70, width * 0.32, stage_h * 0.26)
        art.draw_string_lights(
            c, left + width * 0.16, stage_bottom + stage_h * 0.82, left + width * 0.84, stage_bottom + stage_h * 0.86, bulbs=5
        )
    elif mission_id == "mission_07":
        art.draw_tree(c, left + width * 0.02, stage_bottom + stage_h * 0.50, width * 0.14, stage_h * 0.26)
        art.draw_deer(c, left + width * 0.80, stage_bottom + stage_h * 0.72, width * 0.14, stage_h * 0.18)
        art.draw_creek(c, left + width * 0.16, stage_bottom + stage_h * 0.78, width * 0.68, stage_h * 0.12)
    elif mission_id == "mission_08":
        art.draw_window(c, left + width * 0.36, stage_bottom + stage_h * 0.76, width * 0.28, stage_h * 0.18)
        art.draw_cloud(c, left + width * 0.08, stage_bottom + stage_h * 0.88, width * 0.14)
    else:
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


def _start_finish(
    c: canvas.Canvas,
    mission_id: str,
    page: dict,
    start_x: float,
    start_y: float,
    fin_x: float,
    fin_y: float,
    cell: float,
) -> list[str]:
    drawn: list[str] = []
    if mission_id == "mission_02":
        art.draw_sun(c, start_x - cell * 1.2, start_y + cell * 0.6, cell * 0.7)
        art.draw_moon(c, fin_x + cell * 0.9, fin_y + cell * 1.6, cell * 0.7)
        drawn = ["sunrise_hill", "orchard_maze", "harvest_moon"]
    elif mission_id == "mission_03":
        art.draw_child(c, start_x - cell * 1.35, start_y - cell * 0.2, cell * 2.4, facing=1, hair="bob", lantern=False)
        art.draw_basket(c, start_x - cell * 1.7, start_y - cell * 0.1, cell * 1.1)
        art.draw_table(c, fin_x - cell * 0.4, fin_y + cell * 1.05, cell * 2.6, cell * 1.5)
        drawn = ["child_with_basket", "corn_row_maze", "barn_table"]
    elif mission_id == "mission_04":
        art.draw_child(c, start_x - cell * 1.35, start_y - cell * 0.2, cell * 2.4, facing=1, hair="short", lantern=True)
        art.draw_porch(c, fin_x - cell * 0.4, fin_y + cell * 1.05, cell * 2.8, cell * 2.0, lit=True)
        drawn = ["child_on_path", "woods_maze", "lit_porch"]
    elif mission_id == "mission_05":
        art.draw_basket(c, start_x - cell * 1.6, start_y, cell * 1.4)
        art.draw_porch(c, fin_x - cell * 0.5, fin_y + cell * 1.0, cell * 2.8, cell * 2.0, lit=False)
        drawn = ["extra_basket", "fence_maze", "neighbor_door"]
    elif mission_id == "mission_06":
        art.draw_child(c, start_x - cell * 1.35, start_y - cell * 0.2, cell * 2.4, facing=1, hair="bob", lantern=False)
        art.draw_chair(c, start_x - cell * 2.1, start_y - cell * 0.1, cell * 1.2, cell * 1.8)
        art.draw_table(c, fin_x - cell * 0.4, fin_y + cell * 1.05, cell * 2.6, cell * 1.5)
        drawn = ["child_on_bench", "booth_maze", "game_table"]
    elif mission_id == "mission_07":
        art.circle(c, start_x - cell * 1.1, start_y + cell * 0.4, cell * 0.55, 1.8)
        art.draw_ground(c, fin_x - cell * 0.2, fin_y + cell * 1.1, cell * 2.2, cell * 1.1)
        drawn = ["creek_stone", "creek_bank_maze", "lookout_hill"]
    elif mission_id == "mission_08":
        art.draw_table(c, start_x - cell * 2.2, start_y - cell * 0.1, cell * 1.8, cell * 1.2)
        art.draw_chair(c, fin_x - cell * 0.2, fin_y + cell * 1.05, cell * 1.6, cell * 2.0)
        drawn = ["kitchen_counter", "hallway_maze", "thank_you_chair"]
    else:
        art.draw_child(c, start_x - cell * 1.35, start_y - cell * 0.2, cell * 2.4, facing=1, hair="bob", lantern=True)
        art.draw_table(c, fin_x - cell * 0.4, fin_y + cell * 1.05, cell * 2.6, cell * 1.5)
        drawn = ["child_with_lantern", "hedge_maze", "welcome_table"]
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_PUZZLE_LETTER_PT)
    c.drawCentredString(start_x - cell * 1.35, start_y - cell * 0.55, page["start_label"])
    c.drawCentredString(fin_x + cell * 0.9, fin_y + cell * 2.7, page["finish_label"])
    return [*drawn, "start_label", "finish_label"]


def draw_maze_page(
    c: canvas.Canvas,
    spec: dict,
    maze: Maze,
    *,
    answer_key: bool = False,
    page_number: int = 3,
    marked_proof: bool = False,
    canon: dict | None = None,
    accepted_scene: Path | None = None,
) -> dict:
    mission = _mission_from_spec(spec)
    page = mission["pages"][2]
    reference = (canon or {}).get("reference") or mission.get("scripture_reference") or ""
    title = page["title"] if not answer_key else f"{page['title']} — Answer Key"
    instruction = (
        page["child_instruction"]
        if not answer_key
        else "The dark line is the one unique path through the maze."
    )
    box = live_box(page_number) if marked_proof else None
    content, y = page_header(
        c,
        page_number,
        title,
        instruction,
        kicker=f"{reference}  ·  Follow the path" if reference else "Follow the path",
        box=box,
    )
    left, bottom, right, top = content
    width = right - left
    stage_top = y
    stage_bottom = bottom + 6
    stage_h = stage_top - stage_bottom
    maze_bottom = stage_bottom + stage_h * 0.18
    maze_top = stage_bottom + stage_h * 0.66
    cell = min((width * 0.64) / maze.cols, (maze_top - maze_bottom) / maze.rows)
    maze_w = cell * maze.cols
    maze_h = cell * maze.rows
    x0 = left + (width - maze_w) / 2
    y0 = maze_bottom

    art.ink(c, 1.6)
    c.line(left + 8, y0 - 6, right - 8, y0 - 6)
    if accepted_scene is not None:
        c.drawImage(
            ImageReader(str(accepted_scene)),
            left,
            stage_bottom,
            width=width,
            height=stage_h,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
    else:
        _scenery(c, mission["id"], left, right, stage_bottom, stage_h, width)

    wall = max(2.0, cell * 0.15)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(1, 1, 1)
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

    start_x, start_y = cell_xy(*maze.start)
    fin_x, fin_y = cell_xy(*maze.finish)
    drawn = _start_finish(c, mission["id"], page, start_x, start_y, fin_x, fin_y, cell)

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
        "page": page_number,
        "type": "maze",
        "mission_id": mission["id"],
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": drawn,
        "text_in_artwork": False,
        "placeholder": marked_proof and accepted_scene is None,
        "artwork_status": (
            "accepted"
            if accepted_scene is not None
            else ("placeholder_only" if marked_proof else "procedural_lineart")
        ),
        "asset_integration": (
            "Accepted maze environment ingested behind the code-drawn unique path. "
            "START/FINISH labels remain code-rendered."
            if accepted_scene is not None
            else "Start picture, maze path, and finish picture share one scene. "
            "The unique solution is the maze generator path."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "start": list(maze.start),
        "finish": list(maze.finish),
        "seed": page.get("seed"),
        "grid": list(page.get("grid") or [maze.rows, maze.cols]),
        "path": [list(cell) for cell in maze.solve()] if answer_key else None,
        "drawing_area_sqin": None,
    }
