"""Front-matter templates. Code renders all final type."""

from __future__ import annotations

from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.layout import USED_INSTRUCTION_PT, USED_SUBTITLE_PT, USED_TITLE_PT
from mission_of_words.proof import live_box
from mission_of_words.text import ink_text, wrapped_text

WELCOME_BODY = (
    "This book has eight Fall Faith Missions. Each mission has four pages: a coloring "
    "picture, a Search & Find, a maze, and a faith page where you can check, draw, and pray. "
    "A grown-up can read the short Bible line with you. Then you do the pages. Take your time. "
    "Look carefully. Let your light shine by doing good."
)

PARENT_NOTE = (
    "Bright Hearts is Bible-first, not only Bible-themed. Each mission is locked to one "
    "public-domain 1769 Oxford King James verse. Short quotations appear as source_text. "
    "The child paraphrase is labeled and is never mixed into the Bible wording. We do not "
    "use bulk copyrighted Bible text. Activities help ages 5-8 practice the verse with "
    "pictures, mazes, and drawing. They do not add extra Bible stories. Answer keys for "
    "Search & Find and mazes are in the back. This interior is a technical proof until "
    "accepted artwork replaces the marked placeholders."
)


def draw_title_page(c: canvas.Canvas, book: dict, page_number: int = 1) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    cx = (left + right) / 2
    art.draw_lantern(c, cx - 28, top - 140, 90)
    ink_text(c)
    y = top - 170
    c.setFont("Helvetica-Bold", 26)
    for line in _wrap(c, book["working_title"], width, "Helvetica-Bold", 26):
        c.drawCentredString(cx, y, line)
        y -= 30
    y -= 8
    c.setFont("Helvetica", USED_SUBTITLE_PT)
    y = wrapped_text(c, book["subtitle"], left + 12, y, width - 24, size=USED_SUBTITLE_PT, leading=16)
    y -= 18
    c.setFont("Helvetica", USED_INSTRUCTION_PT)
    c.drawCentredString(cx, y, book.get("audience") or "Ages 5-8")
    y -= 22
    c.drawCentredString(cx, y, "Paperback interior  ·  8.5 × 11 in  ·  black and white")
    y -= 40
    art.draw_heart(c, cx, y, 16)
    y -= 36
    c.setFont("Helvetica-Oblique", USED_INSTRUCTION_PT)
    c.drawCentredString(cx, y, "A Bright Hearts Christian Fall Activity Book")
    y -= 28
    c.setFont("Helvetica", USED_INSTRUCTION_PT)
    c.drawCentredString(cx, bottom + 48, "Text rendered by code. Artwork slots are NON-PRODUCTION placeholders.")
    return _record(page_number, "title", book["working_title"], ["title_lockup"], child=False)


def draw_welcome_page(c: canvas.Canvas, book: dict, page_number: int = 2) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    ink_text(c)
    y = top - 24
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawString(left, y, "Welcome, Bright Hearts")
    y -= 28
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(left, y, "How to use this book")
    y -= 22
    y = wrapped_text(c, WELCOME_BODY, left, y, width, size=USED_INSTRUCTION_PT, leading=18)
    y -= 16
    steps = [
        "1. Look at the mission map. Pick a mission with a grown-up.",
        "2. Color the first picture. Stay inside the live area.",
        "3. Find all 8 items. Circle each one when you see it.",
        "4. Start at START. Follow the path to FINISH.",
        "5. On the faith page, check, draw, and pray.",
    ]
    for step in steps:
        y = wrapped_text(c, step, left, y, width, size=USED_INSTRUCTION_PT, leading=18)
        y -= 6
    art.draw_lantern(c, right - 70, bottom + 24, 64)
    art.draw_child(c, left + 40, bottom + 16, 90, facing=1, hair="bob", lantern=True)
    return _record(
        page_number,
        "welcome",
        "Welcome, Bright Hearts",
        ["welcome_spot"],
        instruction="Read how to use the book, then start Mission 1 with a grown-up.",
    )


def draw_contents_page(c: canvas.Canvas, missions: list[dict], page_number: int = 3) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    ink_text(c)
    y = top - 24
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    c.drawString(left, y, "Fall Faith Missions Map")
    y -= 22
    y = wrapped_text(
        c,
        "Eight unique missions. Each one is locked to a Bible verse. Page numbers show where to begin.",
        left,
        y,
        width,
        size=USED_INSTRUCTION_PT,
        leading=17,
    )
    y -= 10
    for mission in missions:
        start = int(mission["global_page_start"])
        line = f"Mission {mission['sequence']}  p.{start}  {mission['title']}  ·  {mission['scripture_reference']}"
        y = wrapped_text(c, line, left, y, width, font="Helvetica-Bold", size=USED_INSTRUCTION_PT, leading=17)
        y -= 8
        art.draw_heart(c, right - 18, y + 22, 8)
    return _record(
        page_number,
        "contents",
        "Fall Faith Missions Map",
        ["missions_map"],
        instruction="Find your mission on the map, then turn to that page.",
    )


def draw_parent_note_page(c: canvas.Canvas, book: dict, page_number: int = 4) -> dict:
    left, bottom, right, top = live_box(page_number)
    width = right - left
    ink_text(c)
    y = top - 24
    c.setFont("Helvetica-Bold", USED_TITLE_PT)
    y = wrapped_text(c, "A Note for Parents and Caregivers", left, y, width, font="Helvetica-Bold", size=USED_TITLE_PT, leading=24)
    y -= 8
    y = wrapped_text(c, PARENT_NOTE, left, y, width, size=USED_INSTRUCTION_PT, leading=17)
    y -= 14
    c.setFont("Helvetica-Bold", USED_INSTRUCTION_PT)
    c.drawString(left, y, "Bible source note")
    y -= 18
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
    y -= 12
    c.setFont("Helvetica", USED_INSTRUCTION_PT)
    c.drawString(left, y, f"Intended list price baseline: ${book.get('kdp_list_price_usd', 9.99):.2f}")
    return _record(page_number, "parent_note", "A Note for Parents and Caregivers", ["parent_letter"], child=False)


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
) -> dict:
    return {
        "page": page,
        "type": page_type,
        "title": title,
        "required_objects": list(drawn),
        "drawn_objects": list(drawn),
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": "Code-rendered type with marked NON-PRODUCTION placeholder art.",
        "child_instruction": instruction or title,
        "bible_connection": "",
        "drawing_area_sqin": None,
        "child_instruction_required": child,
    }
