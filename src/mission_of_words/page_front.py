"""Front-matter templates. Code renders all final type."""

from __future__ import annotations

from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.brand import SERIES_LINE, WELCOME_HEADING
from mission_of_words.fonts import FONT_BODY, FONT_ITALIC, FONT_TITLE_BOLD
from mission_of_words.layout import USED_INSTRUCTION_PT, USED_SUBTITLE_PT
from mission_of_words.proof import live_box
from mission_of_words.scenes import draw_coloring_scene
from mission_of_words.templates import draw_activity_header
from mission_of_words.text import ink_text, wrapped_text

WELCOME_BODY = (
    "This book has eight Fall Faith Missions. Each mission has four pages: a coloring "
    "picture, a Search & Find, a maze, and a faith page where you can check, draw, and pray. "
    "A grown-up can read the short Bible line with you. Then you do the pages. Take your time. "
    "Look carefully. Let your light shine by doing good."
)

PARENT_NOTE = (
    "Little Lampkeepers is Bible-first, not only Bible-themed. Each mission is locked to one "
    "public-domain 1769 Oxford King James verse. Short quotations appear as source_text. "
    "The child paraphrase is labeled and is never mixed into the Bible wording. We do not "
    "use bulk copyrighted Bible text. Activities help ages 5-8 practice the verse with "
    "pictures, mazes, and drawing. They do not add extra Bible stories. Answer keys for "
    "Search & Find and mazes are in the back."
)


def draw_title_page(c: canvas.Canvas, book: dict, page_number: int = 1) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    cx = (left + right) / 2
    ink_text(c)
    y = top - 8
    c.setFont(FONT_TITLE_BOLD, 13)
    c.drawCentredString(cx, y, SERIES_LINE)
    y -= 28
    c.setFont(FONT_TITLE_BOLD, 26)
    for line in _wrap(c, book["working_title"], width, FONT_TITLE_BOLD, 26):
        c.drawCentredString(cx, y, line)
        y -= 30
    y -= 4
    c.setFont(FONT_BODY, USED_SUBTITLE_PT)
    y = wrapped_text(c, book["subtitle"], left + 12, y, width - 24, size=USED_SUBTITLE_PT, leading=16)
    y -= 10
    c.setFont(FONT_BODY, USED_INSTRUCTION_PT)
    c.drawCentredString(cx, y, book.get("audience") or "Ages 5-8")
    scene_top = y - 16
    draw_coloring_scene(c, "mission_01", (left + 6, bottom + 36, right - 6, scene_top))
    return _record(page_number, "title", book["working_title"], ["title_lockup"], child=False)


def draw_welcome_page(c: canvas.Canvas, book: dict, page_number: int = 2) -> dict:
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title=WELCOME_HEADING,
        activity_title="How to use this book",
        instruction="Read how to use the book, then start Mission 1 with a grown-up.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    y = top - 4
    y = wrapped_text(c, WELCOME_BODY, left, y, width, size=USED_INSTRUCTION_PT, leading=18)
    y -= 16
    steps = [
        ("Read", "Look at the mission map. Pick a mission with a grown-up."),
        ("Color", "Fill the big picture. Stay inside the live area."),
        ("Find", "Circle all 8 hidden gifts in the scene."),
        ("Follow", "Start at START. Follow the path to FINISH."),
        ("Pray", "On the faith page, choose, draw, and pray."),
    ]
    card_h = min(52, (y - bottom - 90) / len(steps) - 8)
    for title, body in steps:
        art.ink(c, 1.5)
        c.roundRect(left, y - card_h, width, card_h, 10, fill=1, stroke=1)
        art.draw_heart(c, left + 22, y - card_h / 2, 8)
        ink_text(c)
        c.setFont(FONT_TITLE_BOLD, USED_INSTRUCTION_PT)
        c.drawString(left + 44, y - 16, title)
        wrapped_text(c, body, left + 44, y - 32, width - 56, size=USED_INSTRUCTION_PT, leading=16)
        y -= card_h + 8
    art.draw_lantern(c, right - 64, bottom + 10, 54)
    art.draw_child(c, left + 36, bottom + 8, 78, facing=1, hair="bob", lantern=True)
    return _record(
        page_number,
        "welcome",
        WELCOME_HEADING,
        ["welcome_spot"],
        instruction="Read how to use the book, then start Mission 1 with a grown-up.",
        layout=plan.state.as_fields(),
    )


def draw_contents_page(c: canvas.Canvas, missions: list[dict], page_number: int = 3) -> dict:
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title="Fall Faith Missions Map",
        activity_title="",
        instruction="Eight unique missions. Each one is locked to a Bible verse. Page numbers show where to begin.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    y = top - 6
    row_h = min(58, (y - bottom - 12) / max(len(missions), 1) - 6)
    for mission in missions:
        start = int(mission["global_page_start"])
        art.ink(c, 1.4)
        c.roundRect(left, y - row_h, width, row_h, 10, fill=1, stroke=1)
        art.draw_star(c, left + 18, y - row_h / 2 + 2, 7)
        ink_text(c)
        c.setFont(FONT_TITLE_BOLD, USED_INSTRUCTION_PT)
        c.drawString(left + 36, y - 16, f"Mission {mission['sequence']}  ·  p.{start}")
        wrapped_text(
            c,
            f"{mission['title']}  ·  {mission['scripture_reference']}",
            left + 36,
            y - 32,
            width - 48,
            font=FONT_ITALIC,
            size=USED_INSTRUCTION_PT,
            leading=15,
        )
        y -= row_h + 6
    return _record(
        page_number,
        "contents",
        "Fall Faith Missions Map",
        ["missions_map"],
        instruction="Find your mission on the map, then turn to that page.",
        layout=plan.state.as_fields(),
    )


def draw_parent_note_page(c: canvas.Canvas, book: dict, page_number: int = 4) -> dict:
    box = live_box(page_number)
    plan = draw_activity_header(
        c,
        page_number,
        mission_title="A Note for Parents and Caregivers",
        activity_title="Bible source note",
        instruction="Little Lampkeepers is Bible-first. Each mission is locked to one public-domain verse.",
        box=box,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    y = top - 4
    y = wrapped_text(c, PARENT_NOTE, left, y, width, size=USED_INSTRUCTION_PT, leading=17)
    y -= 14
    y = wrapped_text(
        c,
        "Translation: 1769 Oxford King James Version. License: public domain in the United States. "
        "Child paraphrase is a separate field. Do not treat lanterns, mazes, or fall props as facts from the verse.",
        left,
        y,
        width,
        size=USED_INSTRUCTION_PT,
        leading=17,
    )
    y -= 16
    c.setFont(FONT_BODY, USED_INSTRUCTION_PT)
    c.drawString(left, y, f"Intended list price baseline: ${book.get('kdp_list_price_usd', 9.99):.2f}")
    art.draw_lantern(c, right - 58, bottom + 12, 48)
    return _record(
        page_number,
        "parent_note",
        "A Note for Parents and Caregivers",
        ["parent_letter"],
        child=False,
        layout=plan.state.as_fields(),
    )


def _wrap(c: canvas.Canvas, text: str, max_width: float, font: str, size: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _record(
    page: int,
    page_type: str,
    title: str,
    drawn: list[str],
    *,
    instruction: str = "",
    child: bool = True,
    layout: dict | None = None,
) -> dict:
    record = {
        "page": page,
        "type": page_type,
        "title": title,
        "required_objects": list(drawn),
        "drawn_objects": list(drawn),
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": "Code-rendered type with a children's-book title scene. Artwork remains a stand-in until accepted GPT2 plates exist.",
        "child_instruction": instruction or title,
        "bible_connection": "",
        "drawing_area_sqin": None,
        "child_instruction_required": child,
    }
    if layout:
        record.update(layout)
    return record
