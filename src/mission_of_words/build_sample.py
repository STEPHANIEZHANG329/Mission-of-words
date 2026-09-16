from __future__ import annotations

import json

from reportlab.pdfgen import canvas

from mission_of_words.bible import bind_mission_canon
from mission_of_words.image_client import paid_call_count
from mission_of_words.layout import (
    PAGE_H,
    PAGE_W,
    USED_ANSWER_KEY_PT,
    USED_INSTRUCTION_PT,
    USED_PUZZLE_LETTER_PT,
    USED_TITLE_PT,
    page_geometry,
    search_find_print_space,
    search_find_scene_rect,
)
from mission_of_words.maze import Maze, generate_maze
from mission_of_words.paths import MISSION_SPEC, OUTPUT_DIR
from mission_of_words.qa import evaluate_build, write_report

CONTENT = MISSION_SPEC
OUTPUT = OUTPUT_DIR


def load_spec() -> dict:
    return json.loads(CONTENT.read_text(encoding="utf-8"))


def _draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font: str = "Helvetica",
    size: int = 12,
    leading: float = 16,
) -> float:
    c.setFont(font, size)
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            line = trial
            continue
        c.drawString(x, y, line)
        y -= leading
        line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def header(c: canvas.Canvas, title: str, subtitle: str | None = None, *, page_number: int = 1) -> None:
    geo = page_geometry(page_number)
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - geo["top_pt"] - 18, title)
    if subtitle:
        c.setFont("Helvetica", USED_INSTRUCTION_PT)
        c.drawCentredString(PAGE_W / 2, PAGE_H - geo["top_pt"] - 38, subtitle)


def draw_coloring_placeholder(c: canvas.Canvas, spec: dict, canon: dict) -> None:
    page = spec["mission"]["pages"][0]
    geo = page_geometry(1)
    header(c, page["title"], canon["reference"], page_number=1)
    y = _draw_wrapped(
        c,
        canon["source_text"],
        geo["left_pt"] + 20,
        PAGE_H - geo["top_pt"] - 62,
        PAGE_W - geo["left_pt"] - geo["right_pt"] - 40,
        size=USED_INSTRUCTION_PT,
    )
    x = geo["left_pt"] + 18
    box_top = y - 10
    box_bottom = geo["bottom_pt"] + 30
    w = PAGE_W - geo["left_pt"] - geo["right_pt"] - 36
    h = box_top - box_bottom
    c.setLineWidth(2)
    c.rect(x, box_bottom, w, h)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(PAGE_W / 2, box_bottom + h / 2 + 10, "ARTWORK PLACEHOLDER")
    c.setFont("Helvetica", USED_INSTRUCTION_PT)
    c.drawCentredString(
        PAGE_W / 2,
        box_bottom + h / 2 - 12,
        "No paid image was generated. Dry-run control plane only.",
    )


def _target_icon(c: canvas.Canvas, name: str, x: float, y: float, s: float) -> None:
    c.setLineWidth(1.5)
    if name == "lantern":
        c.rect(x, y, s * 0.7, s)
        c.arc(x, y + s * 0.65, x + s * 0.7, y + s * 1.35, 0, 180)
        c.line(x + s * 0.35, y, x + s * 0.35, y + s)
    elif name == "pumpkin":
        c.ellipse(x, y, x + s, y + s * 0.75)
        c.line(x + s * 0.5, y + s * 0.75, x + s * 0.5, y + s)
    elif name == "apple":
        c.circle(x + s * 0.45, y + s * 0.42, s * 0.38)
        c.line(x + s * 0.45, y + s * 0.8, x + s * 0.55, y + s)
    elif name == "leaf":
        c.ellipse(x, y, x + s, y + s * 0.5)
        c.line(x, y, x + s, y + s * 0.5)
    elif name == "acorn":
        c.ellipse(x, y, x + s * 0.65, y + s * 0.8)
        c.line(x, y + s * 0.58, x + s * 0.65, y + s * 0.58)
    elif name == "scarf":
        c.rect(x, y, s * 0.3, s)
        c.rect(x + s * 0.32, y + s * 0.25, s * 0.3, s * 0.75)
    elif name == "basket":
        c.rect(x, y, s, s * 0.6)
        c.arc(x, y + s * 0.25, x + s, y + s * 1.15, 0, 180)
    elif name == "Bible":
        c.rect(x, y, s * 0.9, s * 0.7)
        c.line(x + s * 0.45, y + s * 0.14, x + s * 0.45, y + s * 0.56)
        c.line(x + s * 0.30, y + s * 0.35, x + s * 0.60, y + s * 0.35)
    else:
        c.circle(x + s / 2, y + s / 2, s / 2)


def draw_search_find(c: canvas.Canvas, spec: dict, answer_key: bool = False) -> None:
    page = spec["mission"]["pages"][1]
    geo = page_geometry(2)
    title = page["title"] if not answer_key else "Search & Find — Answer Key"
    header(
        c,
        title,
        page["instruction"] if not answer_key else "Deterministic placement map",
        page_number=2,
    )

    scene = search_find_scene_rect(2)
    scene_x = scene["x_pt"]
    scene_y = scene["y_pt"]
    scene_w = scene["width_pt"]
    scene_h = scene["height_pt"]
    c.setLineWidth(1.5)
    c.rect(scene_x, scene_y, scene_w, scene_h)

    # Simple deterministic placeholder background: ground, church, tree and table.
    c.line(scene_x, scene_y + scene_h * 0.27, scene_x + scene_w, scene_y + scene_h * 0.27)
    c.rect(scene_x + scene_w * 0.08, scene_y + scene_h * 0.28, scene_w * 0.24, scene_h * 0.30)
    c.line(scene_x + scene_w * 0.08, scene_y + scene_h * 0.58, scene_x + scene_w * 0.20, scene_y + scene_h * 0.70)
    c.line(scene_x + scene_w * 0.20, scene_y + scene_h * 0.70, scene_x + scene_w * 0.32, scene_y + scene_h * 0.58)
    c.rect(scene_x + scene_w * 0.70, scene_y + scene_h * 0.28, scene_w * 0.18, scene_h * 0.10)
    c.line(scene_x + scene_w * 0.56, scene_y + scene_h * 0.28, scene_x + scene_w * 0.56, scene_y + scene_h * 0.62)
    c.circle(scene_x + scene_w * 0.56, scene_y + scene_h * 0.68, scene_w * 0.09)

    placements = search_find_print_space(page["targets"])
    for item in placements["targets"]:
        _target_icon(c, item["name"], item["x_pt"], item["y_pt"], item["width_pt"])
        if answer_key:
            c.setLineWidth(1)
            size = item["width_pt"]
            c.circle(item["x_pt"] + size * 0.45, item["y_pt"] + size * 0.45, size * 0.75)
            c.setFont("Helvetica", USED_ANSWER_KEY_PT)
            c.drawString(item["x_pt"], item["y_pt"] + size + 2, item["name"])

    if not answer_key:
        c.setFont("Helvetica", USED_PUZZLE_LETTER_PT)
        labels = " • ".join(t["name"] for t in page["targets"])
        c.drawCentredString(PAGE_W / 2, geo["bottom_pt"] + 54, labels)


def draw_maze(c: canvas.Canvas, maze: Maze, title: str, show_solution: bool = False, *, page_number: int = 3) -> None:
    geo = page_geometry(page_number)
    header(c, title, "Start → Finish", page_number=page_number)
    box_x = geo["left_pt"] + 32
    box_y = geo["bottom_pt"] + 55
    box_w = PAGE_W - geo["left_pt"] - geo["right_pt"] - 64
    box_h = PAGE_H - geo["top_pt"] - geo["bottom_pt"] - 125
    cell = min(box_w / maze.cols, box_h / maze.rows)
    maze_w = cell * maze.cols
    maze_h = cell * maze.rows
    x0 = (PAGE_W - maze_w) / 2
    y0 = box_y + (box_h - maze_h) / 2

    c.setLineWidth(1.5)
    for r in range(maze.rows):
        for col in range(maze.cols):
            x = x0 + col * cell
            y = y0 + (maze.rows - 1 - r) * cell
            here = (r, col)
            linked = maze.passages[here]
            if (r - 1, col) not in linked:
                c.line(x, y + cell, x + cell, y + cell)
            if (r + 1, col) not in linked:
                c.line(x, y, x + cell, y)
            if (r, col - 1) not in linked:
                c.line(x, y, x, y + cell)
            if (r, col + 1) not in linked:
                c.line(x + cell, y, x + cell, y + cell)

    c.setFont("Helvetica-Bold", USED_PUZZLE_LETTER_PT)
    c.drawString(x0 + 3, y0 + maze_h + 6, "START")
    c.drawRightString(x0 + maze_w - 3, y0 - 15, "FINISH")

    if show_solution:
        path = maze.solve()
        c.setLineWidth(3)
        points = []
        for r, col in path:
            px = x0 + (col + 0.5) * cell
            py = y0 + (maze.rows - r - 0.5) * cell
            points.append((px, py))
        for a, b in zip(points, points[1:]):
            c.line(a[0], a[1], b[0], b[1])


def draw_faith_page(c: canvas.Canvas, spec: dict, canon: dict) -> None:
    page = spec["mission"]["pages"][3]
    geo = page_geometry(4)
    header(c, page["title"], canon["reference"], page_number=4)
    y = PAGE_H - geo["top_pt"] - 70
    c.setFont("Helvetica", USED_INSTRUCTION_PT)
    c.drawString(geo["left_pt"] + 20, y, "For kids (not scripture):")
    y = _draw_wrapped(
        c,
        canon["child_paraphrase"],
        geo["left_pt"] + 20,
        y - 18,
        PAGE_W - geo["left_pt"] - geo["right_pt"] - 40,
        size=USED_INSTRUCTION_PT,
    )
    y -= 8
    c.setFont("Helvetica-Bold", 14)
    c.drawString(geo["left_pt"] + 20, y, "Check one:")
    y -= 28
    c.setFont("Helvetica", 13)
    for item in page["checkboxes"]:
        c.rect(geo["left_pt"] + 26, y - 2, 13, 13)
        c.drawString(geo["left_pt"] + 50, y, item)
        y -= 28

    c.setFont("Helvetica-Bold", 14)
    c.drawString(geo["left_pt"] + 20, y - 4, page["drawing_prompt"])
    draw_y = y - 210
    c.setLineWidth(1.5)
    c.rect(geo["left_pt"] + 20, draw_y, PAGE_W - geo["left_pt"] - geo["right_pt"] - 40, 170)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(geo["left_pt"] + 20, draw_y - 40, "Prayer:")
    c.setFont("Helvetica", 13)
    c.drawString(geo["left_pt"] + 80, draw_y - 40, page["prayer"])


def build() -> dict:
    spec = load_spec()
    canon = bind_mission_canon(spec)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sample_path = OUTPUT / "BrightHearts_ShineYourLight_Phase0.pdf"
    answer_path = OUTPUT / "BrightHearts_ShineYourLight_AnswerKey.pdf"

    maze_page = spec["mission"]["pages"][2]
    rows, cols = maze_page["grid"]
    maze = generate_maze(rows=rows, cols=cols, seed=maze_page["seed"])

    c = canvas.Canvas(str(sample_path), pagesize=(PAGE_W, PAGE_H))
    draw_coloring_placeholder(c, spec, canon)
    c.showPage()
    draw_search_find(c, spec, answer_key=False)
    c.showPage()
    draw_maze(c, maze, maze_page["title"], show_solution=False, page_number=3)
    c.showPage()
    draw_faith_page(c, spec, canon)
    c.save()

    a = canvas.Canvas(str(answer_path), pagesize=(PAGE_W, PAGE_H))
    draw_search_find(a, spec, answer_key=True)
    a.showPage()
    draw_maze(a, maze, "Maze — Answer Key", show_solution=True, page_number=3)
    a.save()

    qa = evaluate_build(spec=spec, maze=maze, paid_image_calls=paid_call_count(), sample_pages=4)
    write_report(qa)
    return qa


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2))
    if not result["technical_pass"]:
        raise SystemExit(1)
