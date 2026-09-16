"""Back-matter templates, including compact answer keys derived from activity manifests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.layout import USED_ANSWER_KEY_PT, USED_INSTRUCTION_PT, USED_TITLE_PT
from mission_of_words.maze import Maze
from mission_of_words.proof import live_box
from mission_of_words.targets import display_name
from mission_of_words.text import ink_text, wrapped_text

CERTIFICATE_LINE = "This certifies that ________________________ completed the Bright Hearts Fall missions."
DATE_LINE = "Date ________________________    Grown-up ________________________"


def draw_answer_key_page(
    c: canvas.Canvas,
    *,
    page_number: int,
    mission: dict,
    canon: dict,
    search_composed: Path,
    search_manifest: list[dict],
    maze: Maze,
) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    ink_text(c)
    y = top - 18
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawString(left, y, f"Answer Key: {mission['title']}")
    y -= 18
    c.setFont("Helvetica", USED_ANSWER_KEY_PT)
    c.drawString(left, y, f"{canon['reference']}  ·  Answers come from the same search manifest and maze path as the child pages.")
    y -= 16

    mid = (left + right) / 2
    search_h = (y - bottom) * 0.52
    c.setFont("Helvetica-Bold", USED_ANSWER_KEY_PT)
    c.drawString(left, y, "Search & Find")
    y -= 12
    scene_top = y
    scene_bottom = y - search_h + 8
    scene_w = width * 0.62
    scene_h = scene_top - scene_bottom
    c.drawImage(
        ImageReader(str(search_composed)),
        left,
        scene_bottom,
        width=scene_w,
        height=scene_h,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    with Image.open(search_composed) as composed_image:
        img_w, img_h = composed_image.size
    scale = min(scene_w / img_w, scene_h / img_h)
    draw_w, draw_h = img_w * scale, img_h * scale
    ox = left + (scene_w - draw_w) / 2
    oy = scene_bottom + (scene_h - draw_h) / 2
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1.1)
    c.setFont("Helvetica", USED_ANSWER_KEY_PT)
    for row in search_manifest:
        cx = ox + (row["x"] + row["width"] / 2) * scale
        cy = oy + (img_h - (row["y"] + row["height"] / 2)) * scale
        radius = max(row["width"], row["height"]) * scale * 0.58
        c.circle(cx, cy, radius, fill=0, stroke=1)

    list_x = left + scene_w + 12
    ly = scene_top
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_ANSWER_KEY_PT)
    c.drawString(list_x, ly, "Targets")
    ly -= 12
    c.setFont("Helvetica", USED_ANSWER_KEY_PT)
    for index, row in enumerate(search_manifest, start=1):
        c.drawString(list_x, ly, f"{index}. {display_name(row['name'])}")
        ly -= 11

    maze_top = scene_bottom - 14
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_ANSWER_KEY_PT)
    c.drawString(left, maze_top, "Maze path")
    maze_bottom = bottom + 8
    rows, cols = maze.rows, maze.cols
    cell = min((width * 0.72) / cols, (maze_top - 12 - maze_bottom) / rows)
    x0 = left + (width - cell * cols) / 2
    y0 = maze_bottom
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(max(0.9, cell * 0.12))
    for r in range(rows):
        for col in range(cols):
            x, y_cell = x0 + col * cell, y0 + r * cell
            linked = maze.passages[(r, col)]
            if (r + 1, col) not in linked:
                c.line(x, y_cell + cell, x + cell, y_cell + cell)
            if (r - 1, col) not in linked:
                c.line(x, y_cell, x + cell, y_cell)
            if (r, col - 1) not in linked:
                c.line(x, y_cell, x, y_cell + cell)
            if (r, col + 1) not in linked:
                c.line(x + cell, y_cell, x + cell, y_cell + cell)
    path = maze.solve()
    c.setLineWidth(max(1.6, cell * 0.18))
    points = [(x0 + (col + 0.5) * cell, y0 + (r + 0.5) * cell) for r, col in path]
    for a, b in zip(points, points[1:]):
        c.line(a[0], a[1], b[0], b[1])

    search_page = mission["global_page_start"] + 1
    maze_page = mission["global_page_start"] + 2
    return {
        "page": page_number,
        "type": "answer_key",
        "mission_id": mission["id"],
        "required_objects": ["search_answer", "maze_answer"],
        "drawn_objects": ["search_answer", "maze_answer"],
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": (
            "Search circles use the compositor manifest. Maze line uses the unique generated path."
        ),
        "child_instruction": "Answer key for grown-ups. Type is 9 pt.",
        "bible_connection": canon["reference"],
        "answers_activity_pages": [search_page, maze_page],
        "search_manifest": search_manifest,
        "maze_path": [list(cell) for cell in path],
        "drawing_area_sqin": None,
    }


def draw_gratitude_journal(c: canvas.Canvas, page_number: int = 45) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    ink_text(c)
    y = top - 22
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawString(left, y, "Gratitude Journal")
    y -= 24
    y = wrapped_text(
        c,
        "Draw or write three things you thank God for. Do this with a grown-up. This page is not a copy of a mission page.",
        left,
        y,
        width,
        size=USED_INSTRUCTION_PT,
        leading=17,
    )
    y -= 8
    box_h = (y - bottom - 20) / 3 - 8
    for index, prompt in enumerate(("Thank You for...", "Thank You for...", "Thank You for..."), start=1):
        top_box = y - (index - 1) * (box_h + 12)
        art.ink(c, 1.6)
        c.roundRect(left, top_box - box_h, width, box_h, 12, fill=1, stroke=1)
        ink_text(c)
        c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
        c.drawString(left + 12, top_box - 18, f"{index}. {prompt}")
    return {
        "page": page_number,
        "type": "bonus_activity",
        "required_objects": ["bonus_activity"],
        "drawn_objects": ["bonus_activity"],
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": "Three unique thank-you drawing boxes, not a copied mission faith page.",
        "child_instruction": "Draw or write three things you thank God for.",
        "bible_connection": "Psalm 107:1",
        "drawing_area_sqin": (width / 72.0) * (box_h / 72.0) * 3,
    }


def draw_prayer_walk(c: canvas.Canvas, page_number: int = 46) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    ink_text(c)
    y = top - 22
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawString(left, y, "A Prayer Walk Together")
    y -= 24
    y = wrapped_text(
        c,
        "Walk outside with a grown-up. Notice what God made. Then pray the short lines. This is a parent-child bonus, not a maze.",
        left,
        y,
        width,
        size=USED_INSTRUCTION_PT,
        leading=17,
    )
    y -= 8
    prompts = [
        "I notice ________________________",
        "I notice ________________________",
        "I notice ________________________",
        "I notice ________________________",
        "Prayer: God, thank You for making a world that is very good.",
        "Prayer: Jesus, help me give thanks in every part of this day.",
    ]
    for prompt in prompts:
        art.ink(c, 1.4)
        c.roundRect(left, y - 36, width, 40, 8, fill=1, stroke=1)
        ink_text(c)
        c.setFont("Helvetica", USED_INSTRUCTION_PT)
        c.drawString(left + 12, y - 22, prompt)
        y -= 48
    art.draw_leaf(c, right - 70, bottom + 16, 36)
    return {
        "page": page_number,
        "type": "bonus_activity",
        "required_objects": ["bonus_activity"],
        "drawn_objects": ["bonus_activity"],
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": "Outdoor noticing plus prayer prompts. Unique from the gratitude journal.",
        "child_instruction": "Walk outside with a grown-up. Notice four things God made, then pray.",
        "bible_connection": "1 Thessalonians 5:18",
        "drawing_area_sqin": None,
    }


def draw_certificate(c: canvas.Canvas, book: dict, page_number: int = 47) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    art.ink(c, 2.2)
    c.roundRect(left, bottom, width, top - bottom, 18, fill=1, stroke=1)
    cx = (left + right) / 2
    art.draw_lantern(c, cx - 24, top - 100, 70)
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawCentredString(cx, top - 130, "Bright Hearts Completion Certificate")
    y = wrapped_text(c, CERTIFICATE_LINE, left + 24, top - 170, width - 48, size=USED_INSTRUCTION_PT, leading=18)
    y -= 24
    y = wrapped_text(c, DATE_LINE, left + 24, y, width - 48, size=USED_INSTRUCTION_PT, leading=18)
    y -= 28
    wrapped_text(
        c,
        "Keep shining God's light by doing good. Write your name. A grown-up can sign with you.",
        left + 24,
        y,
        width - 48,
        size=USED_INSTRUCTION_PT,
        leading=17,
    )
    art.draw_heart(c, cx, bottom + 48, 16)
    return {
        "page": page_number,
        "type": "certificate",
        "required_objects": ["certificate_frame"],
        "drawn_objects": ["certificate_frame"],
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": "Code-rendered certificate type inside a marked placeholder frame.",
        "child_instruction": "Write your name and the date on the certificate.",
        "bible_connection": "",
        "drawing_area_sqin": None,
    }


def draw_closing_page(c: canvas.Canvas, book: dict, page_number: int = 48) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    cx = (left + right) / 2
    art.draw_child(c, cx - 80, bottom + 40, 140, facing=1, hair="bob", lantern=True)
    art.draw_child(c, cx + 80, bottom + 40, 140, facing=-1, hair="short", lantern=True)
    ink_text(c)
    y = top - 36
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawCentredString(cx, y, "Keep Shining, Bright Hearts")
    y -= 36
    y = wrapped_text(
        c,
        "You finished eight unique missions. The story of this book is not a new Bible story. "
        "It is practice: let your light shine by doing good, give thanks, share, be kind, and remember God is with you.",
        left + 12,
        y,
        width - 24,
        size=USED_INSTRUCTION_PT,
        leading=18,
    )
    y -= 16
    wrapped_text(
        c,
        book["working_title"] + "  ·  Not a copy of the title page. Go do one good thing today.",
        left + 12,
        y,
        width - 24,
        size=USED_INSTRUCTION_PT,
        leading=17,
    )
    return {
        "page": page_number,
        "type": "closing",
        "required_objects": ["closing_lockup"],
        "drawn_objects": ["closing_lockup"],
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": "Closing lockup is distinct from the title page.",
        "child_instruction": "Remember one way you can shine God's light this week.",
        "bible_connection": "Matthew 5:16",
        "drawing_area_sqin": None,
    }
