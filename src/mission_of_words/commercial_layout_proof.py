"""Zero-cost 48-page commercial layout proof.

Purpose: prove page architecture before any paid image generation. This module
uses only deterministic/procedural art and code-rendered text. It intentionally
optimizes for the Owner-approved commercial reference standard: large integrated
illustration windows, clear hierarchy, readable activities, and no engineering-
worksheet look.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, black, white
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.bible import bind_mission_record
from mission_of_words.book_manifest import load_book_record, load_mission_records
from mission_of_words.layout import PAGE_H, PAGE_W, content_box
from mission_of_words.maze import generate_maze
from mission_of_words.page_search import build_search_scene_from_page
from mission_of_words.render import contact_sheet_grid, render_pdf_pages
from mission_of_words.scenes import draw_coloring_scene
from mission_of_words.templates import draw_maze_grid

OUT = Path("output/commercial_layout")
PDF = OUT / "LittleLampkeepers_48_Page_Commercial_Layout_Proof.pdf"
REPORT = OUT / "layout_report.json"
PREVIEWS = OUT / "previews"
ASSETS = OUT / "assets"

INK = Color(0.08, 0.08, 0.08)
SOFT = Color(0.94, 0.94, 0.94)
MID = Color(0.72, 0.72, 0.72)


def _ink(c: canvas.Canvas, width: float = 1.4) -> None:
    c.setStrokeColor(INK)
    c.setFillColor(white)
    c.setLineWidth(width)
    c.setLineJoin(1)
    c.setLineCap(1)


def _panel(c: canvas.Canvas, box: tuple[float, float, float, float], radius: float = 14, width: float = 1.5) -> None:
    left, bottom, right, top = box
    _ink(c, width)
    c.roundRect(left, bottom, right - left, top - bottom, radius, fill=1, stroke=1)


def _wrap(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list[str]:
    words = str(text or "").split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if c.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_lines(c: canvas.Canvas, lines: list[str], x: float, y: float, *, font: str, size: float, leading: float, centered: bool = False, width: float = 0) -> float:
    c.setFillColor(INK)
    c.setFont(font, size)
    cursor = y
    for line in lines:
        if centered:
            c.drawCentredString(x + width / 2, cursor, line)
        else:
            c.drawString(x, cursor, line)
        cursor -= leading
    return cursor


def _footer(c: canvas.Canvas, page_number: int, left: float, bottom: float, right: float) -> None:
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(right, bottom - 18, str(page_number))


def _mission_kicker(c: canvas.Canvas, mission: dict, page_number: int, *, activity: str, title: str | None = None) -> tuple[float, float, float, float]:
    left, bottom, right, top = content_box(page_number)
    width = right - left
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(left, top - 2, f"MISSION {mission['sequence']}  |  {activity.upper()}")
    c.setFont("Helvetica-Bold", 25)
    display = title or mission["title"]
    lines = _wrap(c, display, "Helvetica-Bold", 25, width * 0.78)
    y = top - 34
    y = _draw_lines(c, lines, left, y, font="Helvetica-Bold", size=25, leading=28)
    c.setFont("Helvetica-Oblique", 10.5)
    c.drawRightString(right, top - 4, mission["scripture_reference"])
    return left, bottom, right, y - 6


def _instruction(c: canvas.Canvas, text: str, left: float, y: float, width: float, *, size: float = 12.5) -> float:
    lines = _wrap(c, text, "Helvetica", size, width)
    return _draw_lines(c, lines, left, y, font="Helvetica", size=size, leading=size + 3)


def _title_page(c: canvas.Canvas, book: dict, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 31)
    c.drawCentredString((left + right) / 2, top - 34, "Little Lampkeepers")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString((left + right) / 2, top - 68, "Shine Your Light This Fall")
    c.setFont("Helvetica", 12.5)
    c.drawCentredString((left + right) / 2, top - 92, "A Christian Fall Activity Book for Kids Ages 5-8")
    scene = (left + 8, bottom + 90, right - 8, top - 128)
    draw_coloring_scene(c, "mission_01", scene)
    ribbon = (left + 42, bottom + 24, right - 42, bottom + 70)
    _panel(c, ribbon, radius=20, width=1.8)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString((left + right) / 2, bottom + 43, "COLOR  |  SEARCH  |  MAZE  |  THINK  |  PRAY  |  GROW")
    _footer(c, page_number, left, bottom, right)


def _welcome_page(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString((left + right) / 2, top - 24, "Welcome, Little Lampkeeper!")
    intro = "Every mission connects a Bible truth to something you can color, solve, notice, choose, or pray about."
    _draw_lines(c, _wrap(c, intro, "Helvetica", 13, right - left - 50), left + 25, top - 58, font="Helvetica", size=13, leading=18, centered=True, width=right - left - 50)
    cards = [
        ("1", "READ", "Read the Bible truth together."),
        ("2", "PLAY", "Complete the activity."),
        ("3", "THINK", "Talk about one real-life choice."),
        ("4", "DO", "Put faith into action this week."),
    ]
    y = top - 140
    for number, head, body in cards:
        box = (left + 28, y - 74, right - 28, y)
        _panel(c, box, radius=16, width=1.6)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(left + 58, y - 45, number)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(left + 92, y - 28, head)
        c.setFont("Helvetica", 11.5)
        c.drawString(left + 92, y - 49, body)
        y -= 90
    art.draw_heart(c, (left + right) / 2, bottom + 92, 20)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString((left + right) / 2, bottom + 48, "Small hearts can make a bright difference.")
    _footer(c, page_number, left, bottom, right)


def _contents_page(c: canvas.Canvas, missions: list[dict], page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString((left + right) / 2, top - 24, "Eight Fall Faith Missions")
    y = top - 78
    for mission in missions:
        start = mission["global_page_start"]
        _panel(c, (left + 12, y - 54, right - 12, y), radius=12, width=1.2)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left + 30, y - 23, f"Mission {mission['sequence']}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left + 120, y - 23, mission["title"])
        c.setFont("Helvetica", 10)
        c.drawRightString(right - 30, y - 23, f"pages {start}-{start + 3}")
        c.setFont("Helvetica-Oblique", 9.5)
        c.drawString(left + 120, y - 41, mission["scripture_reference"])
        y -= 64
    _footer(c, page_number, left, bottom, right)


def _parent_page(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString((left + right) / 2, top - 24, "For Parents and Grown-Ups")
    text = "Use each four-page mission as a short screen-free faith moment. Read the Bible reference, let your child explore the activity, then use the final page as a simple conversation and prayer prompt."
    _draw_lines(c, _wrap(c, text, "Helvetica", 12.5, right - left - 70), left + 35, top - 70, font="Helvetica", size=12.5, leading=17, centered=True, width=right - left - 70)
    notes = [
        ("Bible-first", "Every mission connects the activity to a specific Bible truth."),
        ("Kid-sized", "Directions are short, type stays readable, and pages are designed for ages 5-8."),
        ("Screen-free", "Pencils and crayons are ideal; place scrap paper behind marker pages."),
        ("Talk together", "There is no single perfect answer on the Faith in Action page."),
    ]
    y = top - 150
    for head, body in notes:
        _panel(c, (left + 28, y - 74, right - 28, y), radius=15, width=1.4)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(left + 48, y - 25, head)
        c.setFont("Helvetica", 10.5)
        for j, line in enumerate(_wrap(c, body, "Helvetica", 10.5, right - left - 190)):
            c.drawString(left + 150, y - 25 - j * 14, line)
        y -= 90
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawCentredString((left + right) / 2, bottom + 32, "Bible quotations and references are source-locked in the project canon records.")
    _footer(c, page_number, left, bottom, right)


def _coloring_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int) -> None:
    left, bottom, right, y = _mission_kicker(c, mission, page_number, activity="Color and Reflect")
    verse = canon.get("child_paraphrase") or canon.get("source_text") or ""
    y = _instruction(c, verse, left, y, right - left, size=11.5) - 8
    think_h = 74
    scene = (left, bottom + think_h + 16, right, y)
    draw_coloring_scene(c, mission["id"], scene)
    think = (left, bottom, right, bottom + think_h)
    _panel(c, think, radius=16, width=1.6)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(left + 16, bottom + 48, "THINK ABOUT IT")
    prompt = mission["pages"][3]["drawing_prompt"] if mission["pages"][3].get("drawing_prompt") else mission["pages"][0]["bible_connection"]
    c.setFont("Helvetica", 11)
    lines = _wrap(c, prompt, "Helvetica", 11, right - left - 34)
    _draw_lines(c, lines[:2], left + 16, bottom + 28, font="Helvetica", size=11, leading=14)
    _footer(c, page_number, left, bottom, right)


def _legend_icon(c: canvas.Canvas, name: str, x: float, y: float) -> None:
    key = name.lower()
    if key == "lantern": art.draw_lantern(c, x - 8, y - 10, 22)
    elif key == "pumpkin": art.draw_pumpkin(c, x, y, 16)
    elif key == "apple": art.draw_apple(c, x, y, 15)
    elif key == "leaf": art.draw_leaf(c, x - 6, y - 7, 16)
    elif key == "acorn": art.draw_acorn(c, x - 6, y - 7, 15)
    elif key == "scarf": art.draw_scarf(c, x - 6, y - 7, 16)
    elif key == "basket": art.draw_basket(c, x - 8, y - 8, 18)
    elif key == "bible": art.draw_bible(c, x - 8, y - 10, 18)
    else: art.draw_star(c, x, y, 8)


def _search_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int, cache: dict) -> None:
    page = mission["pages"][1]
    left, bottom, right, y = _mission_kicker(c, mission, page_number, activity="Search and Find", title=page["title"])
    y = _instruction(c, page["child_instruction"], left, y, right - left, size=11.5) - 6
    legend_h = 76
    legend = (left, y - legend_h, right, y)
    _panel(c, legend, radius=14, width=1.4)
    targets = [row["name"] for row in page["targets"]]
    col_w = (right - left - 24) / 4
    for index, name in enumerate(targets):
        col = index % 4
        row = index // 4
        cx = left + 18 + col * col_w
        cy = y - 24 - row * 31
        _legend_icon(c, name, cx + 8, cy + 5)
        c.setFont("Helvetica", 9.2)
        c.drawString(cx + 25, cy + 1, name.title())
    scene_top = legend[1] - 10
    scene = (left, bottom, right, scene_top)
    asset_dir = ASSETS / mission["id"]
    composed, manifest, _records = build_search_scene_from_page(
        page,
        asset_dir,
        page_number=page_number,
        theme=mission["id"],
        marked_proof=False,
        status="procedural_lineart",
        mission=mission,
        canon=canon,
    )
    cache[mission["id"]] = {"composed": composed, "manifest": manifest}
    _panel(c, scene, radius=14, width=1.5)
    c.drawImage(ImageReader(str(composed)), scene[0] + 5, scene[1] + 5, width=scene[2] - scene[0] - 10, height=scene[3] - scene[1] - 10, preserveAspectRatio=True, anchor="c", mask="auto")
    _footer(c, page_number, left, bottom, right)


def _maze_scene_decor(c: canvas.Canvas, mission_id: str, box: tuple[float, float, float, float]) -> None:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_cloud(c, left + w * 0.04, top - 40, w * 0.16)
    art.draw_cloud(c, right - w * 0.22, top - 48, w * 0.15)
    art.draw_ground(c, left, bottom, w, h * 0.16)
    if mission_id in {"mission_01", "mission_06"}:
        art.draw_church(c, left + 4, top - h * 0.28, w * 0.17, h * 0.20)
        art.draw_string_lights(c, left + w * 0.72, top - h * 0.10, right - 12, top - h * 0.04, bulbs=5)
    elif mission_id in {"mission_02", "mission_03"}:
        art.draw_tree(c, left + 4, bottom + 8, w * 0.16, h * 0.30)
        art.draw_barn(c, right - w * 0.22, top - h * 0.27, w * 0.20, h * 0.18)
    elif mission_id == "mission_04":
        art.draw_tree(c, left + 4, bottom + 8, w * 0.16, h * 0.34)
        art.draw_porch(c, right - w * 0.22, top - h * 0.28, w * 0.20, h * 0.20, lit=True)
    elif mission_id == "mission_05":
        art.draw_basket(c, left + 8, bottom + 12, 34)
        art.draw_porch(c, right - w * 0.22, top - h * 0.28, w * 0.20, h * 0.20, lit=False)
    elif mission_id == "mission_07":
        art.draw_tree(c, left + 4, bottom + 8, w * 0.16, h * 0.32)
        art.draw_deer(c, right - w * 0.20, bottom + 14, w * 0.14, h * 0.14)
    else:
        art.draw_table(c, left + 8, bottom + 10, w * 0.16, h * 0.09)
        art.draw_window(c, right - w * 0.18, top - h * 0.22, w * 0.14, h * 0.12)


def _maze_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int, cache: dict) -> None:
    page = mission["pages"][2]
    left, bottom, right, y = _mission_kicker(c, mission, page_number, activity="Mission Maze", title=page["title"])
    y = _instruction(c, page["child_instruction"], left, y, right - left, size=11.5) - 4
    scene = (left, bottom, right, y)
    _maze_scene_decor(c, mission["id"], scene)
    rows, cols = page["grid"]
    maze = generate_maze(rows=rows, cols=cols, seed=int(page["seed"]))
    cache.setdefault(mission["id"], {})["maze"] = maze
    sx, sy, sr, st = scene
    w, h = sr - sx, st - sy
    window = (sx + w * 0.13, sy + h * 0.14, sr - w * 0.13, st - h * 0.14)
    _panel(c, window, radius=18, width=2.0)
    pad = 18
    inner_w = window[2] - window[0] - 2 * pad
    inner_h = window[3] - window[1] - 2 * pad
    cell = min(inner_w / cols, inner_h / rows)
    x0 = window[0] + (window[2] - window[0] - cols * cell) / 2
    y0 = window[1] + (window[3] - window[1] - rows * cell) / 2
    draw_maze_grid(c, maze, x0=x0, y0=y0, cell=cell, answer_key=False)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(window[0] + 10, window[3] + 5, "START")
    c.drawRightString(window[2] - 10, window[1] - 13, "FINISH")
    _footer(c, page_number, left, bottom, right)


def _choice_icon(c: canvas.Canvas, icon: str, x: float, y: float) -> None:
    key = str(icon).lower()
    if key in {"help", "share", "kind", "friend", "include", "family", "people"}:
        art.draw_heart(c, x, y, 10)
    elif key in {"leaf", "plant", "bird"}:
        art.draw_leaf(c, x - 6, y - 8, 16)
    elif key in {"apple", "meal", "bread"}:
        art.draw_apple(c, x, y, 13)
    else:
        art.draw_star(c, x, y, 8)


def _faith_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int) -> None:
    page = mission["pages"][3]
    left, bottom, right, y = _mission_kicker(c, mission, page_number, activity="Faith in Action", title=page["title"])
    paraphrase = canon.get("child_paraphrase") or page["bible_connection"]
    callout_h = 62
    _panel(c, (left, y - callout_h, right, y), radius=16, width=1.4)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(left + 14, y - 18, "BIBLE TRUTH")
    _draw_lines(c, _wrap(c, paraphrase, "Helvetica", 10.5, right - left - 28)[:2], left + 14, y - 36, font="Helvetica", size=10.5, leading=13)
    y -= callout_h + 12
    gap = 10
    card_w = (right - left - gap) / 2
    card_h = 62
    choices = page["choices"]
    for index, choice in enumerate(choices):
        col = index % 2
        row = index // 2
        x = left + col * (card_w + gap)
        top = y - row * (card_h + gap)
        box = (x, top - card_h, x + card_w, top)
        _panel(c, box, radius=14, width=1.3)
        c.rect(x + 12, top - 26, 13, 13, fill=0, stroke=1)
        _choice_icon(c, choice.get("icon", ""), x + card_w - 24, top - 29)
        c.setFont("Helvetica-Bold", 10.5)
        lines = _wrap(c, choice["label"], "Helvetica-Bold", 10.5, card_w - 70)
        _draw_lines(c, lines[:2], x + 34, top - 22, font="Helvetica-Bold", size=10.5, leading=13)
    y -= 2 * (card_h + gap) + 8
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(left, y, page["drawing_prompt"])
    y -= 12
    prayer_h = 52
    draw_box = (left, bottom + prayer_h + 10, right, y)
    _panel(c, draw_box, radius=18, width=1.7)
    # A subtle lantern/heart motif keeps the drawing area from feeling like an empty worksheet.
    art.draw_lantern(c, (left + right) / 2 - 24, (bottom + prayer_h + 10 + y) / 2 - 32, 64)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString((left + right) / 2, bottom + prayer_h + 24, "Draw or write your idea here")
    prayer = (left, bottom, right, bottom + prayer_h)
    _panel(c, prayer, radius=14, width=1.4)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(left + 14, bottom + 33, "PRAYER")
    c.setFont("Helvetica", 10.5)
    c.drawString(left + 70, bottom + 33, page["prayer"])
    _footer(c, page_number, left, bottom, right)


def _answer_key_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int, cache: dict) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left, top - 6, f"Mission {mission['sequence']} Answer Key")
    c.setFont("Helvetica", 10.5)
    c.drawString(left, top - 26, mission["title"])
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawRightString(right, top - 26, mission["scripture_reference"])
    split = bottom + (top - bottom) * 0.51
    search_box = (left, split + 10, right, top - 52)
    maze_box = (left, bottom, right, split - 8)
    _panel(c, search_box, radius=14, width=1.4)
    _panel(c, maze_box, radius=14, width=1.4)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(search_box[0] + 12, search_box[3] - 18, "SEARCH AND FIND")
    c.drawString(maze_box[0] + 12, maze_box[3] - 18, "MAZE SOLUTION")
    search = cache[mission["id"]]
    composed = search["composed"]
    manifest = search["manifest"]
    image_box = (search_box[0] + 12, search_box[1] + 12, search_box[2] - 12, search_box[3] - 30)
    with Image.open(composed) as im:
        iw, ih = im.size
    frame_w = image_box[2] - image_box[0]
    frame_h = image_box[3] - image_box[1]
    scale = min(frame_w / iw, frame_h / ih)
    dw, dh = iw * scale, ih * scale
    ox = image_box[0] + (frame_w - dw) / 2
    oy = image_box[1] + (frame_h - dh) / 2
    c.drawImage(ImageReader(str(composed)), ox, oy, width=dw, height=dh, preserveAspectRatio=True, anchor="c", mask="auto")
    for index, row in enumerate(manifest, start=1):
        cx = ox + (row["x"] + row["width"] / 2) * scale
        cy = oy + (ih - (row["y"] + row["height"] / 2)) * scale
        radius = max(10, max(row["width"], row["height"]) * scale * 0.56)
        c.setLineWidth(1.6)
        c.circle(cx, cy, radius, fill=0, stroke=1)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx, cy + radius + 2, str(index))
    maze = search["maze"]
    rows, cols = maze.rows, maze.cols
    inner = (maze_box[0] + 34, maze_box[1] + 28, maze_box[2] - 34, maze_box[3] - 34)
    cell = min((inner[2] - inner[0]) / cols, (inner[3] - inner[1]) / rows)
    x0 = inner[0] + ((inner[2] - inner[0]) - cols * cell) / 2
    y0 = inner[1] + ((inner[3] - inner[1]) - rows * cell) / 2
    draw_maze_grid(c, maze, x0=x0, y0=y0, cell=cell, answer_key=True)
    _footer(c, page_number, left, bottom, right)


def _journal(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString((left + right) / 2, top - 20, "My Gratitude Journal")
    c.setFont("Helvetica", 11.5)
    c.drawCentredString((left + right) / 2, top - 46, "Today I thank God for...")
    y = top - 92
    for _ in range(10):
        art.draw_heart(c, left + 12, y + 3, 5)
        c.line(left + 34, y, right, y)
        y -= 50
    _footer(c, page_number, left, bottom, right)


def _prayers(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString((left + right) / 2, top - 20, "My Prayers")
    c.setFont("Helvetica", 11.5)
    c.drawCentredString((left + right) / 2, top - 46, "People, places, and things I can pray about")
    y = top - 92
    for _ in range(9):
        c.circle(left + 14, y + 3, 4, fill=0, stroke=1)
        c.line(left + 34, y, right, y)
        y -= 54
    art.draw_cross(c, (left + right) / 2 - 3, bottom + 36, 20)
    _footer(c, page_number, left, bottom, right)


def _certificate(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    _panel(c, (left + 10, bottom + 10, right - 10, top - 10), radius=22, width=2.0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString((left + right) / 2, top - 72, "You Are a Light!")
    c.setFont("Helvetica", 13)
    c.drawCentredString((left + right) / 2, top - 102, "Certificate of Completion")
    art.draw_heart(c, (left + right) / 2, top - 155, 18)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString((left + right) / 2, top - 205, "This certifies that")
    c.line(left + 95, top - 244, right - 95, top - 244)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString((left + right) / 2, top - 286, "completed Little Lampkeepers: Shine Your Light This Fall")
    c.setFont("Helvetica", 11)
    c.drawCentredString((left + right) / 2, bottom + 110, "Keep shining through kindness, courage, gratitude, sharing, and prayer.")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString((left + right) / 2, bottom + 62, "Matthew 5:16")
    _footer(c, page_number, left, bottom, right)


def _closing(c: canvas.Canvas, page_number: int) -> None:
    left, bottom, right, top = content_box(page_number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 29)
    c.drawCentredString((left + right) / 2, top - 34, "Keep Shining!")
    scene = (left + 10, bottom + 100, right - 10, top - 82)
    draw_coloring_scene(c, "mission_01", scene)
    _panel(c, (left + 50, bottom + 22, right - 50, bottom + 74), radius=20, width=1.6)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString((left + right) / 2, bottom + 48, "FAITH  |  KINDNESS  |  COURAGE  |  GRATITUDE  |  LOVE")
    _footer(c, page_number, left, bottom, right)


def build() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    book = load_book_record()
    missions = load_mission_records()
    canons = {mission["id"]: bind_mission_record(mission) for mission in missions}
    cache: dict = {}
    c = canvas.Canvas(str(PDF), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Little Lampkeepers - 48 Page Commercial Layout Proof")

    _title_page(c, book, 1); c.showPage()
    _welcome_page(c, 2); c.showPage()
    _contents_page(c, missions, 3); c.showPage()
    _parent_page(c, 4); c.showPage()

    for mission in missions:
        canon = canons[mission["id"]]
        start = int(mission["global_page_start"])
        _coloring_page(c, mission, canon, start); c.showPage()
        _search_page(c, mission, canon, start + 1, cache); c.showPage()
        _maze_page(c, mission, canon, start + 2, cache); c.showPage()
        _faith_page(c, mission, canon, start + 3); c.showPage()

    for mission in missions:
        _answer_key_page(c, mission, canons[mission["id"]], 36 + int(mission["sequence"]), cache)
        c.showPage()

    _journal(c, 45); c.showPage()
    _prayers(c, 46); c.showPage()
    _certificate(c, 47); c.showPage()
    _closing(c, 48); c.showPage()
    c.save()

    previews = render_pdf_pages(PDF, PREVIEWS, dpi=130, prefix="page")
    contact = PREVIEWS / "contact_sheet.png"
    contact_sheet_grid(previews, contact, columns=6)
    contact_sheet_grid(previews[4:20], PREVIEWS / "missions_1_4.png", columns=4)
    contact_sheet_grid(previews[20:36], PREVIEWS / "missions_5_8.png", columns=4)
    report = {
        "status": "PASS_LAYOUT_PROOF_CREATED" if len(previews) == 48 else "FAIL",
        "paid_image_calls": 0,
        "page_count": len(previews),
        "trim_inches": [8.5, 11.0],
        "brand": "Little Lampkeepers",
        "product": "Shine Your Light This Fall",
        "proof_only": True,
        "gpt2_allowed": False,
        "contact_sheet": str(contact),
        "pdf": str(PDF),
        "commercial_layout_principles": [
            "large integrated art window",
            "single clear title hierarchy",
            "scene-first search and find",
            "maze embedded in illustrated scene",
            "faith page with visual cards plus large response area",
            "answer keys readable at print size",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    build()
