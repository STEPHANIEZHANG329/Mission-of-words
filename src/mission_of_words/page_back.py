"""Back-matter templates, including usable answer keys derived from activity manifests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.brand import CERTIFICATE_HEADING, CERTIFICATE_LINE, CLOSING_HEADING
from mission_of_words.geometry import BBox
from mission_of_words.layout import USED_ANSWER_KEY_PT, USED_INSTRUCTION_PT, USED_TITLE_PT
from mission_of_words.maze import Maze
from mission_of_words.proof import live_box
from mission_of_words.targets import display_name
from mission_of_words.templates import (
    draw_activity_header,
    draw_answer_number,
    draw_maze_grid,
    draw_panel,
    draw_start_finish_badges,
)
from mission_of_words.text import ink_text, wrapped_text

DATE_LINE = "Date ________________________    Grown-up ________________________"
ANSWER_LIST_PT = max(USED_ANSWER_KEY_PT, 11)


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
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_number=int(mission.get("sequence") or 1),
        mission_title=str(mission.get("title") or ""),
        activity_title="Answer Key",
        reference=str(canon.get("reference") or ""),
        activity_label="Search & Find  +  Maze",
        instruction="Answers come from the same search manifest and unique maze path as the child pages.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    ink_text(c)
    c.setFont("Helvetica-Bold", 12)
    heading_y = top - 12
    c.drawString(left, heading_y, "Search & Find")
    plan.state.add(BBox("search_heading", left, heading_y - 3, left + 90, heading_y + 10, kind="text"))

    list_w = min(150, width * 0.28)
    scene_w = width - list_w - 10
    scene_h = (top - bottom) * 0.62
    scene_top = heading_y - 14
    scene_bottom = scene_top - scene_h
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
    for index, row in enumerate(search_manifest, start=1):
        cx = ox + (row["x"] + row["width"] / 2) * scale
        cy = oy + (img_h - (row["y"] + row["height"] / 2)) * scale
        radius = max(row["width"], row["height"]) * scale * 0.58
        draw_answer_number(c, cx, cy, max(radius, 10), index, plan.state, f"ak_search_{row['name']}")

    list_x = left + scene_w + 10
    ly = scene_top - 4
    ink_text(c)
    c.setFont("Helvetica-Bold", ANSWER_LIST_PT)
    c.drawString(list_x, ly, "Targets")
    ly -= 16
    c.setFont("Helvetica", ANSWER_LIST_PT)
    for index, row in enumerate(search_manifest, start=1):
        label = f"{index}. {display_name(row['name'])}"
        c.drawString(list_x, ly, label)
        plan.state.add(
            BBox(
                f"ak_list_{row['name']}",
                list_x,
                ly - 2,
                list_x + c.stringWidth(label, "Helvetica", ANSWER_LIST_PT),
                ly + ANSWER_LIST_PT,
                kind="text",
            )
        )
        ly -= 15

    maze_top = scene_bottom - 14
    ink_text(c)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, maze_top, "Maze path  ·  the dark line is the only way")
    maze_bottom = bottom + 6
    window = (left, maze_bottom, right, maze_top - 14)
    draw_panel(c, window, radius=12, width=1.8)
    win_left, win_bottom, win_right, win_top = window
    pad = 12
    rows, cols = maze.rows, maze.cols
    cell = min((win_right - win_left - 2 * pad) / cols, (win_top - win_bottom - 2 * pad) / rows)
    x0 = win_left + (win_right - win_left - cell * cols) / 2
    y0 = win_bottom + (win_top - win_bottom - cell * rows) / 2
    path = maze.solve()
    draw_maze_grid(c, maze, x0=x0, y0=y0, cell=cell, answer_key=True, solution_weight=max(2.8, cell * 0.30))
    draw_start_finish_badges(
        c,
        plan.state,
        start_xy=(win_left + 36, win_bottom + 14),
        finish_xy=(win_right - 36, win_top - 14),
        start_label="START",
        finish_label="FINISH",
        cell=cell,
    )

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
            "Search numbers use the compositor manifest. Maze line uses the unique generated path."
        ),
        "child_instruction": "Answer key for grown-ups.",
        "bible_connection": canon["reference"],
        "answers_activity_pages": [search_page, maze_page],
        "search_manifest": search_manifest,
        "maze_path": [list(cell) for cell in path],
        "drawing_area_sqin": None,
        **plan.state.as_fields(),
    }


def draw_gratitude_journal(c: canvas.Canvas, page_number: int = 45) -> dict:
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title="Gratitude Journal",
        activity_title="",
        instruction="Draw or write three things you thank God for. Do this with a grown-up.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    box_h = (top - bottom - 24) / 3 - 8
    for index, prompt in enumerate(("Thank You for...", "Thank You for...", "Thank You for..."), start=1):
        top_box = top - (index - 1) * (box_h + 12)
        art.ink(c, 1.6)
        c.roundRect(left, top_box - box_h, width, box_h, 12, fill=1, stroke=1)
        ink_text(c)
        c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
        c.drawString(left + 12, top_box - 18, f"{index}. {prompt}")
        plan.state.add(BBox(f"gratitude_{index}", left, top_box - box_h, left + width, top_box, kind="card"))
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
        **plan.state.as_fields(),
    }


def draw_prayer_walk(c: canvas.Canvas, page_number: int = 46) -> dict:
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title="A Prayer Walk Together",
        activity_title="",
        instruction="Walk outside with a grown-up. Notice what God made. Then pray the short lines.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    y = top - 4
    prompts = [
        "I notice ________________________",
        "I notice ________________________",
        "I notice ________________________",
        "I notice ________________________",
        "Prayer: God, thank You for making a world that is very good.",
        "Prayer: Jesus, help me give thanks in every part of this day.",
    ]
    row_h = min(48, (y - bottom - 20) / len(prompts) - 8)
    for index, prompt in enumerate(prompts):
        art.ink(c, 1.4)
        c.roundRect(left, y - row_h, width, row_h + 4, 8, fill=1, stroke=1)
        ink_text(c)
        c.setFont("Helvetica", USED_INSTRUCTION_PT)
        c.drawString(left + 12, y - row_h + 12, prompt)
        plan.state.add(BBox(f"walk_{index}", left, y - row_h, left + width, y + 4, kind="card"))
        y -= row_h + 10
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
        **plan.state.as_fields(),
    }


def draw_certificate(c: canvas.Canvas, book: dict, page_number: int = 47) -> dict:
    box = live_box(page_number)
    left, bottom, right, top = box
    width = right - left
    art.ink(c, 2.2)
    c.roundRect(left, bottom, width, top - bottom, 18, fill=1, stroke=1)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title=CERTIFICATE_HEADING,
        activity_title="",
        instruction="Write your name and the date on the certificate.",
        box=(left + 18, bottom + 18, right - 18, top - 18),
    )
    cx = (left + right) / 2
    art.draw_lantern(c, cx - 24, plan.y_below - 70, 60)
    y = plan.y_below - 90
    y = wrapped_text(c, CERTIFICATE_LINE, left + 36, y, width - 72, size=USED_INSTRUCTION_PT, leading=18)
    y -= 20
    y = wrapped_text(c, DATE_LINE, left + 36, y, width - 72, size=USED_INSTRUCTION_PT, leading=18)
    y -= 20
    wrapped_text(
        c,
        "Keep shining God's light by doing good. Write your name. A grown-up can sign with you.",
        left + 36,
        y,
        width - 72,
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
        **plan.state.as_fields(),
    }


def draw_closing_page(c: canvas.Canvas, book: dict, page_number: int = 48) -> dict:
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title=CLOSING_HEADING,
        activity_title="",
        instruction="Remember one way you can shine God's light this week.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    cx = (left + right) / 2
    art.draw_child(c, cx - 80, bottom + 24, 140, facing=1, hair="bob", lantern=True)
    art.draw_child(c, cx + 80, bottom + 24, 140, facing=-1, hair="short", lantern=True)
    wrapped_text(
        c,
        "You finished eight unique missions. The story of this book is not a new Bible story. "
        "It is practice: let your light shine by doing good, give thanks, share, be kind, and remember God is with you. "
        + book["working_title"]
        + "  ·  Not a copy of the title page. Go do one good thing today.",
        left + 8,
        top - 8,
        width - 16,
        size=USED_INSTRUCTION_PT,
        leading=18,
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
        **plan.state.as_fields(),
    }
