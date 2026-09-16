"""Illustrated maze pages. The maze sits in a window inside one scene."""

from __future__ import annotations

from pathlib import Path

from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.fonts import FONT_BODY
from mission_of_words.layout import USED_PUZZLE_LETTER_PT
from mission_of_words.maze import Maze
from mission_of_words.proof import live_box
from mission_of_words.composition import maze_embed, maze_path_box, maze_path_min_ratio
from mission_of_words.templates import (
    draw_activity_header,
    draw_maze_grid,
    draw_start_finish_badges,
    place_raster,
)
from mission_of_words.text import ink_text


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def _scenery(c: canvas.Canvas, mission_id: str, box: tuple[float, float, float, float]) -> None:
    """Full-frame decorative surround, not a strip pasted under the maze."""
    left, bottom, right, top = box
    width, height = right - left, top - bottom
    art.draw_cloud(c, left + width * 0.06, top - height * 0.10, width * 0.18)
    art.draw_cloud(c, left + width * 0.74, top - height * 0.12, width * 0.16)
    art.draw_ground(c, left, bottom, width, height * 0.18)
    if mission_id == "mission_02":
        art.draw_sun(c, left + width * 0.12, top - height * 0.08, width * 0.05)
        art.draw_moon(c, right - width * 0.12, top - height * 0.10, width * 0.045)
        art.draw_tree(c, left + 4, bottom + height * 0.12, width * 0.16, height * 0.42)
        art.draw_tree(c, right - width * 0.18, bottom + height * 0.14, width * 0.16, height * 0.40)
    elif mission_id == "mission_03":
        art.draw_barn(c, left + width * 0.02, top - height * 0.42, width * 0.18, height * 0.28)
        art.draw_wheat(c, left + width * 0.04, bottom + height * 0.16, height * 0.16)
        art.draw_wheat(c, right - width * 0.10, bottom + height * 0.16, height * 0.16)
    elif mission_id == "mission_04":
        art.draw_tree(c, left + 4, bottom + height * 0.14, width * 0.16, height * 0.46)
        art.draw_tree(c, right - width * 0.18, bottom + height * 0.14, width * 0.16, height * 0.44)
        art.draw_porch(c, right - width * 0.28, top - height * 0.36, width * 0.22, height * 0.22, lit=True)
    elif mission_id == "mission_05":
        art.draw_porch(c, left + 8, top - height * 0.38, width * 0.22, height * 0.22, lit=False)
        art.draw_tree(c, right - width * 0.18, bottom + height * 0.14, width * 0.16, height * 0.40)
    elif mission_id == "mission_06":
        art.draw_booth(c, left + 6, top - height * 0.40, width * 0.22, height * 0.24)
        art.draw_string_lights(c, left + width * 0.24, top - height * 0.08, right - width * 0.24, top - height * 0.04, bulbs=6)
        art.draw_chair(c, right - width * 0.16, bottom + height * 0.14, width * 0.08, height * 0.16)
    elif mission_id == "mission_07":
        art.draw_tree(c, left + 4, bottom + height * 0.16, width * 0.16, height * 0.40)
        art.draw_deer(c, right - width * 0.20, bottom + height * 0.18, width * 0.14, height * 0.16)
        art.draw_creek(c, left + width * 0.18, bottom + 8, width * 0.64, height * 0.10)
    elif mission_id == "mission_08":
        art.draw_window(c, left + 10, top - height * 0.32, width * 0.16, height * 0.16)
        art.draw_table(c, right - width * 0.24, bottom + height * 0.14, width * 0.18, height * 0.12)
    else:
        art.draw_church(c, left + 6, top - height * 0.40, width * 0.20, height * 0.28)
        art.draw_tree(c, right - width * 0.18, bottom + height * 0.14, width * 0.16, height * 0.40)
        art.draw_string_lights(
            c, left + width * 0.22, top - height * 0.10, left + width * 0.40, top - height * 0.04, bulbs=4
        )


def _start_finish_art(
    c: canvas.Canvas,
    mission_id: str,
    start_x: float,
    start_y: float,
    fin_x: float,
    fin_y: float,
    cell: float,
) -> list[str]:
    if mission_id == "mission_02":
        art.draw_sun(c, start_x - cell * 1.6, start_y + cell * 0.2, cell * 0.55)
        art.draw_moon(c, fin_x + cell * 1.1, fin_y + cell * 0.9, cell * 0.55)
        return ["sunrise_hill", "orchard_maze", "harvest_moon"]
    if mission_id == "mission_03":
        art.draw_child(c, start_x - cell * 1.55, start_y - cell * 0.15, cell * 2.1, facing=1, hair="bob", lantern=False)
        art.draw_basket(c, start_x - cell * 1.9, start_y - cell * 0.05, cell * 0.9)
        art.draw_table(c, fin_x + cell * 0.9, fin_y + cell * 0.2, cell * 2.0, cell * 1.2)
        return ["child_with_basket", "corn_row_maze", "barn_table"]
    if mission_id == "mission_04":
        art.draw_child(c, start_x - cell * 1.55, start_y - cell * 0.15, cell * 2.1, facing=1, hair="short", lantern=True)
        art.draw_porch(c, fin_x + cell * 0.8, fin_y + cell * 0.15, cell * 2.2, cell * 1.6, lit=True)
        return ["child_on_path", "woods_maze", "lit_porch"]
    if mission_id == "mission_05":
        art.draw_basket(c, start_x - cell * 1.8, start_y, cell * 1.2)
        art.draw_porch(c, fin_x + cell * 0.8, fin_y + cell * 0.1, cell * 2.2, cell * 1.6, lit=False)
        return ["extra_basket", "fence_maze", "neighbor_door"]
    if mission_id == "mission_06":
        art.draw_child(c, start_x - cell * 1.55, start_y - cell * 0.15, cell * 2.1, facing=1, hair="bob", lantern=False)
        art.draw_table(c, fin_x + cell * 0.9, fin_y + cell * 0.2, cell * 2.0, cell * 1.2)
        return ["child_on_bench", "booth_maze", "game_table"]
    if mission_id == "mission_07":
        art.circle(c, start_x - cell * 1.2, start_y + cell * 0.35, cell * 0.45, 1.8)
        art.draw_ground(c, fin_x + cell * 0.8, fin_y + cell * 0.2, cell * 1.8, cell * 0.9)
        return ["creek_stone", "creek_bank_maze", "lookout_hill"]
    if mission_id == "mission_08":
        art.draw_table(c, start_x - cell * 2.4, start_y - cell * 0.1, cell * 1.6, cell * 1.0)
        art.draw_chair(c, fin_x + cell * 0.9, fin_y + cell * 0.15, cell * 1.3, cell * 1.7)
        return ["kitchen_counter", "hallway_maze", "thank_you_chair"]
    art.draw_child(c, start_x - cell * 1.55, start_y - cell * 0.15, cell * 2.1, facing=1, hair="bob", lantern=True)
    art.draw_table(c, fin_x + cell * 0.9, fin_y + cell * 0.2, cell * 2.0, cell * 1.2)
    return ["child_with_lantern", "hedge_maze", "welcome_table"]


def draw_maze_page(
    c: canvas.Canvas,
    spec: dict,
    maze: Maze,
    *,
    answer_key: bool = False,
    page_number: int = 3,
    marked_proof: bool = False,
    canon: dict | None = None,
    artwork_path: Path | None = None,
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
    plan = draw_activity_header(
        c,
        page_number,
        mission_number=int(mission.get("sequence") or 1),
        mission_title=str(mission.get("title") or ""),
        activity_title=title,
        reference=str(reference),
        activity_label="Follow the path" if not answer_key else "Maze solution",
        instruction=instruction,
        box=box,
    )
    art_box = plan.art_box
    left, bottom, right, top = art_box
    if artwork_path and Path(artwork_path).is_file():
        place_raster(c, Path(artwork_path), art_box, plan.state, name="maze_surround")
    else:
        _scenery(c, mission["id"], art_box)

    embed = maze_embed(mission["id"])
    path_box = maze_path_box(art_box)
    win_left, win_bottom, win_right, win_top = path_box
    inner_w = win_right - win_left
    inner_h = win_top - win_bottom
    cell = min(inner_w / maze.cols, inner_h / maze.rows)
    maze_w = cell * maze.cols
    maze_h = cell * maze.rows
    x0 = win_left + (win_right - win_left - maze_w) / 2
    y0 = win_bottom + (win_top - win_bottom - maze_h) / 2
    draw_maze_grid(c, maze, x0=x0, y0=y0, cell=cell, answer_key=answer_key, wall_style=embed)

    start_x, start_y = x0 + maze.start[1] * cell, y0 + maze.start[0] * cell + cell * 0.5
    fin_x, fin_y = x0 + maze.finish[1] * cell + cell, y0 + maze.finish[0] * cell + cell * 0.5
    drawn = _start_finish_art(c, mission["id"], start_x, start_y, fin_x, fin_y, cell)
    draw_start_finish_badges(
        c,
        plan.state,
        start_xy=(x0 + cell * 0.5, y0 - 10),
        finish_xy=(x0 + maze_w - cell * 0.5, y0 + maze_h + 12),
        start_label=page["start_label"],
        finish_label=page["finish_label"],
        cell=max(cell, 22),
    )
    path_ratio = (win_top - win_bottom) / max(top - bottom, 1.0)
    if path_ratio < maze_path_min_ratio():
        plan.state.overflow.append(
            f"maze path occupies {path_ratio:.0%} of the scene; floor is {maze_path_min_ratio():.0%}"
        )
    ink_text(c)
    c.setFont(FONT_BODY, USED_PUZZLE_LETTER_PT)

    return {
        "page": page_number,
        "type": "maze",
        "mission_id": mission["id"],
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": [*drawn, "start_label", "finish_label"],
        "text_in_artwork": False,
        "placeholder": marked_proof,
        "artwork_status": "placeholder_only" if marked_proof else "procedural_lineart",
        "asset_integration": (
            f"The maze is the {embed.replace('_', ' ')} through one illustrated environment. "
            "Start and finish pictures belong to that scene; the unique solution is the generator path."
        ),
        "maze_embed": embed,
        "maze_path_ratio": path_ratio,
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "start": list(maze.start),
        "finish": list(maze.finish),
        "seed": page.get("seed"),
        "grid": list(page.get("grid") or [maze.rows, maze.cols]),
        "path": [list(cell) for cell in maze.solve()] if answer_key else None,
        "drawing_area_sqin": None,
        **plan.state.as_fields(),
    }
