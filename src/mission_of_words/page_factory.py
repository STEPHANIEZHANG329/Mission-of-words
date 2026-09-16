"""New page composition factory.

This replaces the rejected worksheet templates. Final type is code-rendered
in children's-publishing faces. Artwork slots are labeled geometry only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words.bibles import hiding_zones_for, mission_recipe
from mission_of_words.geometry import BBox, LayoutState, line_bbox, measuring_canvas, new_state, wrap_lines
from mission_of_words.layout import (
    USED_ANSWER_KEY_PT,
    USED_INSTRUCTION_LEADING,
    USED_INSTRUCTION_PT,
    content_box,
)
from mission_of_words.maze import Maze
from mission_of_words.maze_environment import draw_environment_maze
from mission_of_words.proof import live_box
from mission_of_words.targets import display_name
from mission_of_words.text import ink_text
from mission_of_words.typefaces import BODY, BODY_BOLD, BODY_ITALIC, DISPLAY, KICKER_BOLD, PRAYER, register

INK = Color(0.09, 0.09, 0.09)
SLOT = Color(0.91, 0.91, 0.88)
BAND = Color(0.84, 0.84, 0.80)
ACCENT = Color(0.18, 0.18, 0.18)
CALLOUT = Color(0.12, 0.12, 0.12)


@dataclass
class HeaderPlan:
    state: LayoutState
    art_box: tuple[float, float, float, float]
    footer_box: BBox
    y_below: float
    header_fraction: float
    art_fraction: float


def _content(page_number: int, box: tuple[float, float, float, float] | None) -> tuple[float, float, float, float]:
    return box or live_box(page_number)


def hatch_slot(c: canvas.Canvas, box: tuple[float, float, float, float], label: str) -> None:
    left, bottom, right, top = box
    c.setFillColor(SLOT)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.6)
    c.rect(left, bottom, right - left, top - bottom, fill=1, stroke=1)
    c.setStrokeColor(Color(0.72, 0.72, 0.68))
    c.setLineWidth(0.6)
    step = 14
    x = left
    while x < right + (top - bottom):
        c.line(x, bottom, x - (top - bottom), top)
        x += step
    ink_text(c)
    c.setFillColor(INK)
    c.setFont(BODY_BOLD, 9)
    c.drawCentredString((left + right) / 2, (bottom + top) / 2 - 4, label)


def depth_bands(c: canvas.Canvas, box: tuple[float, float, float, float], labels: tuple[str, str, str]) -> None:
    left, bottom, right, top = box
    h = top - bottom
    bands = (
        (bottom, bottom + h * 0.28, labels[0], Color(0.88, 0.88, 0.84)),
        (bottom + h * 0.28, bottom + h * 0.68, labels[1], Color(0.92, 0.92, 0.89)),
        (bottom + h * 0.68, top, labels[2], Color(0.86, 0.86, 0.82)),
    )
    for y0, y1, text, fill in bands:
        c.setFillColor(fill)
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.1)
        c.rect(left, y0, right - left, y1 - y0, fill=1, stroke=1)
        ink_text(c)
        c.setFillColor(INK)
        c.setFont(BODY, 9)
        c.drawString(left + 8, (y0 + y1) / 2 - 3, text)


def plan_header(
    c: canvas.Canvas,
    page_number: int,
    *,
    kicker: str,
    title: str,
    reference: str = "",
    instruction: str = "",
    header_fraction: float = 0.14,
    instruction_fraction: float = 0.0,
    box: tuple[float, float, float, float] | None = None,
    draw: bool = True,
    instruction_in_header: bool = False,
) -> HeaderPlan:
    register()
    left, bottom, right, top = _content(page_number, box)
    width = right - left
    height = top - bottom
    state = new_state(page_number, (left, bottom, right, top))
    header_h = height * header_fraction
    instr_h = height * instruction_fraction if instruction and not instruction_in_header else 0
    header_bottom = top - header_h
    art_bottom = bottom + instr_h
    art_box = (left, art_bottom, right, header_bottom)
    art_fraction = (header_bottom - art_bottom) / height if height else 0

    footer = BBox("page_number", right - 28, bottom, right, bottom + 12, kind="folio")
    state.add(footer)
    if draw:
        ink_text(c)
        c.setFillColor(INK)
        c.setFont(BODY_BOLD, 10)
        c.drawRightString(right, bottom + 1, str(page_number))

    y = top - 4
    if kicker:
        font, size, lead = KICKER_BOLD, 10, 12
        lines, overflow = wrap_lines(c, kicker, font, size, width)
        state.overflow.extend(overflow)
        for index, line in enumerate(lines):
            baseline = y - size
            box_line = line_bbox(f"mission_badge:{index}" if index == 0 else f"kicker:{index}", left, baseline, line, font, size, c, kind="badge")
            state.add(box_line)
            if draw:
                ink_text(c)
                c.setFillColor(INK)
                c.setFont(font, size)
                c.drawString(left, baseline, line)
            y -= lead
        y -= 3

    title_pt = 20
    title_lead = 23
    lines, overflow = wrap_lines(c, title, DISPLAY, title_pt, width)
    state.overflow.extend(overflow)
    for index, line in enumerate(lines):
        baseline = y - title_pt * 0.82
        box_line = line_bbox(f"mission_title:{index}", left, baseline, line, DISPLAY, title_pt, c)
        state.add(box_line)
        if draw:
            ink_text(c)
            c.setFillColor(INK)
            c.setFont(DISPLAY, title_pt)
            c.drawString(left, baseline, line)
        y -= title_lead
    if reference:
        y -= 2
        font, size = BODY_ITALIC, 11
        lines, overflow = wrap_lines(c, reference, font, size, width)
        state.overflow.extend(overflow)
        for index, line in enumerate(lines):
            baseline = y - size * 0.85
            box_line = line_bbox(f"reference:{index}", left, baseline, line, font, size, c)
            state.add(box_line)
            if draw:
                ink_text(c)
                c.setFillColor(INK)
                c.setFont(font, size)
                c.drawString(left, baseline, line)
            y -= size + 3

    if instruction and instruction_in_header:
        y -= 4
        font, size, lead = BODY, USED_INSTRUCTION_PT, USED_INSTRUCTION_LEADING
        lines, overflow = wrap_lines(c, instruction, font, size, width)
        state.overflow.extend(overflow)
        for index, line in enumerate(lines):
            baseline = y - size * 0.85
            box_line = line_bbox(f"instruction:{index}", left, baseline, line, font, size, c)
            state.add(box_line)
            if draw:
                ink_text(c)
                c.setFillColor(INK)
                c.setFont(font, size)
                c.drawString(left, baseline, line)
            y -= lead

    if instruction and not instruction_in_header and instr_h:
        font, size, lead = BODY, USED_INSTRUCTION_PT, USED_INSTRUCTION_LEADING
        lines, overflow = wrap_lines(c, instruction, font, size, width)
        state.overflow.extend(overflow)
        y_prompt = bottom + instr_h - 4
        for index, line in enumerate(lines):
            baseline = y_prompt - (index + 1) * lead + 4
            box_line = line_bbox(f"instruction:{index}", left, baseline, line, font, size, c)
            state.add(box_line)
            if draw:
                ink_text(c)
                c.setFillColor(INK)
                c.setFont(font, size)
                c.drawString(left, baseline, line)

    needed_header = max(height * header_fraction, top - y + 8)
    header_bottom = top - needed_header
    art_box = (left, art_bottom, right, header_bottom)
    art_fraction = (header_bottom - art_bottom) / height if height else 0
    return HeaderPlan(
        state=state,
        art_box=art_box,
        footer_box=footer,
        y_below=header_bottom,
        header_fraction=needed_header / height if height else header_fraction,
        art_fraction=art_fraction,
    )


def measure_header(page_number: int, **kwargs) -> HeaderPlan:
    return plan_header(measuring_canvas(), page_number, draw=False, **kwargs)


def _record(page_number: int, page_type: str, mission: dict | None, page: dict | None, plan: HeaderPlan, drawn: list[str], **extra) -> dict:
    required = list((page or {}).get("required_objects") or drawn)
    record = {
        "page": page_number,
        "type": page_type,
        "mission_id": (mission or {}).get("id"),
        "visual_prompt": (page or {}).get("visual_prompt") or "",
        "required_objects": required,
        "drawn_objects": list(dict.fromkeys([*required, *drawn])),
        "text_in_artwork": False,
        "placeholder": True,
        "artwork_status": "placeholder_only",
        "asset_integration": extra.pop("asset_integration", "Internal geometry mock. Publication art is not authorized."),
        "child_instruction": (page or {}).get("child_instruction") or extra.pop("child_instruction", ""),
        "bible_connection": (page or {}).get("bible_connection") or "",
        "drawing_area_sqin": extra.pop("drawing_area_sqin", None),
        "header_fraction": plan.header_fraction,
        "art_fraction": plan.art_fraction,
        "white_window": False,
        **plan.state.as_fields(),
        **extra,
    }
    return record


def draw_hero_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int) -> dict:
    page = mission["pages"][0]
    recipe = mission_recipe(mission["id"])
    hero = recipe["hero"]
    plan = plan_header(
        c,
        page_number,
        kicker=f"Mission {mission['sequence']}  ·  Color this picture",
        title=str(mission.get("title") or page["title"]),
        reference=str(canon.get("reference") or mission.get("scripture_reference") or ""),
        instruction=page["child_instruction"],
        header_fraction=float(hero["header_fraction"]),
        instruction_fraction=float(hero["instruction_fraction"]),
    )
    depth_bands(
        c,
        plan.art_box,
        (
            f"FOREGROUND CAST SLOT  ·  {', '.join(name.title() for name in recipe['cast'])}",
            f"MID SCENE  ·  {recipe['environment']}",
            f"BACKGROUND  ·  {hero['camera']}  ·  NO TEXT IN ART  ·  {hero['art_fraction']*100:.0f}% page",
        ),
    )
    live = live_box(page_number)
    live_h = live[3] - live[1]
    art_h = plan.art_box[3] - plan.art_box[1]
    return _record(
        page_number,
        "coloring",
        mission,
        page,
        plan,
        list(page["required_objects"]) + ["hero_scene"],
        art_fraction=art_h / live_h,
        banner=hero["banner"],
        asset_integration="Hero coloring illustration owns 70-80% of the live area. Type is a compact banner. GPT2 must not draw letters.",
    )


def draw_search_page(
    c: canvas.Canvas,
    mission: dict,
    canon: dict,
    composed_path: Path,
    manifest: list[dict],
    page_number: int,
    *,
    answer_key: bool = False,
) -> dict:
    page = mission["pages"][1]
    recipe = mission_recipe(mission["id"])
    search = recipe["search"]
    instruction = (
        page["child_instruction"]
        if not answer_key
        else "Numbers mark the same independently placed targets used on the child page."
    )
    plan = plan_header(
        c,
        page_number,
        kicker=f"Mission {mission['sequence']}  ·  {'Search & Find answers' if answer_key else 'Search & Find'}",
        title=str(mission.get("title") or ""),
        reference=str(canon.get("reference") or ""),
        instruction=instruction,
        header_fraction=float(search["header_fraction"]),
        instruction_fraction=0.0,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    height = top - bottom
    legend_h = height * float(search["legend_fraction"]) / (float(search["scene_fraction"]) + float(search["legend_fraction"]))
    scene_box = (left, bottom + legend_h, right, top)
    legend_box = (left, bottom, right, bottom + legend_h)
    hatch_slot(c, scene_box, f"SEARCH SCENE  ·  {search['scene_frame']}  ·  targets are code-placed")
    if composed_path and Path(composed_path).is_file():
        c.drawImage(
            ImageReader(str(composed_path)),
            scene_box[0],
            scene_box[1],
            width=scene_box[2] - scene_box[0],
            height=scene_box[3] - scene_box[1],
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
    names = [row["name"] for row in manifest]
    _legend(c, names, legend_box, plan.state)
    raster_meta: dict = {}
    if composed_path and Path(composed_path).is_file():
        with Image.open(composed_path) as image:
            img_w, img_h = image.size
        scene_w = scene_box[2] - scene_box[0]
        scene_h = scene_box[3] - scene_box[1]
        scale = min(scene_w / img_w, scene_h / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        ox = scene_box[0] + (scene_w - draw_w) / 2
        oy = scene_box[1] + (scene_h - draw_h) / 2
        if answer_key:
            for index, row in enumerate(manifest, start=1):
                cx = ox + (row["x"] + row["width"] / 2) * scale
                cy = oy + (img_h - (row["y"] + row["height"] / 2)) * scale
                radius = max(12.0, max(row["width"], row["height"]) * scale * 0.55)
                _callout(c, cx, cy, radius, index)
        raster_meta = {
            "raster_pixel_size": [img_w, img_h],
            "placed_points": [draw_w, draw_h],
            "effective_dpi": min(img_w / (draw_w / 72.0), img_h / (draw_h / 72.0)) if draw_w and draw_h else 0,
            "manifest": manifest,
            "composed_path": str(composed_path),
        }
    live = live_box(page_number)
    live_h = live[3] - live[1]
    return _record(
        page_number,
        "search_find" if not answer_key else "answer_key",
        mission,
        page,
        plan,
        ["search_background", *names],
        legend_fraction=(legend_box[3] - legend_box[1]) / live_h,
        scene_fraction=(scene_box[3] - scene_box[1]) / live_h,
        hiding_zones=hiding_zones_for(mission),
        asset_integration="Rich scene first. Eight independent code targets sit in named hiding zones. Legend is a compact secondary strip.",
        **raster_meta,
    )


def _legend(c: canvas.Canvas, names: list[str], box: tuple[float, float, float, float], state: LayoutState) -> None:
    left, bottom, right, top = box
    c.setFillColor(BAND)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.rect(left, bottom, right - left, top - bottom, fill=1, stroke=1)
    ink_text(c)
    c.setFont(BODY_BOLD, 11)
    heading = "Find:"
    c.drawString(left + 6, top - 13, heading)
    state.add(BBox("legend_heading", left + 6, top - 16, left + 40, top - 2, kind="text"))
    col_w = (right - left - 12) / 4
    for index, name in enumerate(names):
        col = index % 4
        row = index // 4
        x = left + 8 + col * col_w
        y = top - 28 - row * 16
        label = f"{index + 1} {display_name(name)}"
        c.setFont(BODY, 11)
        c.drawString(x, y, label)


def _callout(c: canvas.Canvas, cx: float, cy: float, radius: float, number: int) -> None:
    c.setStrokeColor(CALLOUT)
    c.setFillColor(white)
    c.setLineWidth(2.0)
    c.circle(cx, cy, max(radius, 11), fill=1, stroke=1)
    ink_text(c)
    c.setFont(BODY_BOLD, max(USED_ANSWER_KEY_PT, 11))
    label = str(number)
    c.drawCentredString(cx, cy - 4, label)


def draw_maze_page(
    c: canvas.Canvas,
    mission: dict,
    canon: dict,
    maze: Maze,
    page_number: int,
    *,
    answer_key: bool = False,
) -> dict:
    page = mission["pages"][2]
    recipe = mission_recipe(mission["id"])
    maze_spec = recipe["maze"]
    instruction = page["child_instruction"] if not answer_key else "The dark line is the one unique path through the maze."
    plan = plan_header(
        c,
        page_number,
        kicker=f"Mission {mission['sequence']}  ·  {'Maze solution' if answer_key else 'Follow the path'}",
        title=str(mission.get("title") or ""),
        reference=str(canon.get("reference") or ""),
        instruction=instruction,
        header_fraction=float(maze_spec["header_fraction"]),
        instruction_fraction=0.0,
        instruction_in_header=True,
    )
    meta = draw_environment_maze(
        c,
        maze,
        plan.art_box,
        environment_kind=str(maze_spec["environment_kind"]),
        answer_key=answer_key,
    )
    left, bottom, right, top = plan.art_box
    ink_text(c)
    c.setFont(BODY_BOLD, 12)
    c.drawString(left + 4, bottom + 6, page["start_label"])
    c.drawRightString(right - 4, top - 14, page["finish_label"])
    c.setFont(BODY, 8)
    c.drawCentredString((left + right) / 2, top - 10, f"MAZE IS THE {maze_spec['environment_kind'].replace('_', ' ').upper()}  ·  NO WHITE WINDOW")
    drawn = list(page["required_objects"])
    meta.pop("path", None)
    meta.pop("environment_kind", None)
    return _record(
        page_number,
        "maze",
        mission,
        page,
        plan,
        drawn,
        start=list(maze.start),
        finish=list(maze.finish),
        seed=page.get("seed"),
        grid=list(page.get("grid") or [maze.rows, maze.cols]),
        path=[list(cell) for cell in maze.solve()] if answer_key else None,
        maze_path=[list(cell) for cell in maze.solve()] if answer_key else None,
        environment_kind=maze_spec["environment_kind"],
        asset_integration="The maze is the environment path. Start and finish belong to the scene. No rectangular white window.",
        **meta,
    )


def draw_faith_page(c: canvas.Canvas, mission: dict, canon: dict, page_number: int) -> dict:
    page = mission["pages"][3]
    recipe = mission_recipe(mission["id"])
    faith = recipe["faith"]
    plan = plan_header(
        c,
        page_number,
        kicker=f"Mission {mission['sequence']}  ·  Faith in Action",
        title=page["title"],
        reference=str(canon.get("reference") or ""),
        instruction=page["child_instruction"],
        header_fraction=float(faith["header_fraction"]),
        instruction_fraction=0.0,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    ink_text(c)
    c.setFont(BODY_ITALIC, USED_INSTRUCTION_PT)
    y = top - 4
    paraphrase = canon.get("child_paraphrase") or ""
    lines, overflow = wrap_lines(c, paraphrase, BODY_ITALIC, USED_INSTRUCTION_PT, width)
    plan.state.overflow.extend(overflow)
    for index, line in enumerate(lines):
        baseline = y - USED_INSTRUCTION_PT
        plan.state.add(line_bbox(f"paraphrase:{index}", left, baseline, line, BODY_ITALIC, USED_INSTRUCTION_PT, c))
        c.setFillColor(INK)
        c.setFont(BODY_ITALIC, USED_INSTRUCTION_PT)
        c.drawString(left, baseline, line)
        y -= USED_INSTRUCTION_LEADING
    y -= 8
    choices = page["choices"]
    cards_bottom = _draw_choice_cards(c, plan.state, faith["card_layout"], choices, left, y, right, bottom)
    prayer_h = 48
    draw_bottom = bottom + prayer_h + 8
    draw_top = cards_bottom - 8
    draw_box = (left + width * 0.08, draw_bottom, right - width * 0.08, draw_top)
    hatch_slot(c, draw_box, f"DRAW HERE  ·  {faith['drawing_shape']}")
    plan.state.add(BBox("drawing_area", *draw_box, kind="draw"))
    ink_text(c)
    c.setFont(BODY_BOLD, USED_INSTRUCTION_PT)
    c.drawString(left, draw_top + 2, page["drawing_prompt"][:48])
    prayer_box = (left, bottom, right, bottom + prayer_h)
    c.setFillColor(BAND)
    c.setStrokeColor(ACCENT)
    c.roundRect(left, bottom, width, prayer_h, 10, fill=1, stroke=1)
    ink_text(c)
    c.setFont(PRAYER, 16)
    prayer_lines, overflow = wrap_lines(c, page["prayer"], PRAYER, 16, width - 16)
    plan.state.overflow.extend(overflow)
    py = bottom + prayer_h - 18
    for line in prayer_lines:
        c.drawString(left + 8, py, line)
        py -= 16
    drawing_sqin = ((draw_box[2] - draw_box[0]) / 72.0) * ((draw_box[3] - draw_box[1]) / 72.0)
    return _record(
        page_number,
        "faith_interaction",
        mission,
        page,
        plan,
        list(page["required_objects"]),
        drawing_area_sqin=drawing_sqin,
        checkbox_inches=0.28,
        choice_count=len(choices),
        card_layout=faith["card_layout"],
        asset_integration="Illustrated choice cards, a meaningful drawing shape, and a short prayer. Not a form.",
    )


def _draw_choice_cards(
    c: canvas.Canvas,
    state: LayoutState,
    layout: str,
    choices: list[dict],
    left: float,
    top: float,
    right: float,
    bottom: float,
) -> float:
    width = right - left
    cards_h = 96
    if layout == "lantern_row":
        card_w = (width - 18) / 4
        y = top - cards_h
        for index, choice in enumerate(choices):
            x = left + index * (card_w + 6)
            _card(c, state, index, x, y, card_w, cards_h, choice, radius=18)
        return y
    if layout == "sun_moon_arc":
        card_w = (width - 12) / 2
        y = top - 52
        for index, choice in enumerate(choices):
            col = index % 2
            row = index // 2
            x = left + col * (card_w + 12)
            cy = y - row * 50
            _card(c, state, index, x, cy - 44, card_w, 44, choice, radius=20)
        return y - 96
    if layout == "stepping_stones":
        card_h = 36
        gap = 8
        y = top
        for index, choice in enumerate(choices):
            x = left + index * 16
            cy = y - (index + 1) * (card_h + gap)
            _card(c, state, index, x, cy, width * 0.70, card_h, choice, radius=16)
        return y - 4 * (card_h + gap)
    if layout == "porch_steps":
        y = top
        for index, choice in enumerate(choices):
            inset = index * 10
            cy = y - (index + 1) * 28
            _card(c, state, index, left + inset, cy, width - inset * 2, 26, choice, radius=4)
        return y - 4 * 28
    if layout == "festival_tickets":
        card_w = (width - 12) / 2
        y = top - 50
        for index, choice in enumerate(choices):
            col = index % 2
            row = index // 2
            x = left + col * (card_w + 12)
            _card(c, state, index, x, y - row * 48 - 40, card_w, 40, choice, radius=3)
        return y - 88
    if layout == "leaf_scatter":
        positions = (
            (left, top - 44),
            (right - width * 0.46, top - 44),
            (left, top - 92),
            (right - width * 0.46, top - 92),
        )
        card_w = width * 0.44
        for index, choice in enumerate(choices):
            x, y = positions[index]
            _card(c, state, index, x, y, card_w, 40, choice, radius=16)
        return top - 92
    if layout == "place_settings":
        card_w = (width - 12) / 2
        y = top - 48
        for index, choice in enumerate(choices):
            col = index % 2
            row = index // 2
            x = left + col * (card_w + 12)
            _card(c, state, index, x, y - row * 46 - 38, card_w, 38, choice, radius=8)
        return y - 84
    card_w = (width - 12) / 2
    y = top - 50
    for index, choice in enumerate(choices):
        col = index % 2
        row = index // 2
        x = left + col * (card_w + 12)
        _card(c, state, index, x, y - row * 50 - 42, card_w, 42, choice, radius=12)
    return y - 92


def _card(c: canvas.Canvas, state: LayoutState, index: int, x: float, y: float, w: float, h: float, choice: dict, *, radius: float) -> None:
    c.setFillColor(white)
    c.setStrokeColor(INK)
    c.setLineWidth(1.6)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.rect(x + 8, y + h - 18, 12, 12, fill=0, stroke=1)
    ink_text(c)
    c.setFont(BODY_BOLD, 11)
    label = str(choice["label"])
    lines, _overflow = wrap_lines(c, label, BODY_BOLD, 11, w - 28)
    c.drawString(x + 24, y + h - 16, lines[0])
    state.add(BBox(f"choice_{index}", x, y, x + w, y + h, kind="card"))


def draw_title_page(c: canvas.Canvas, book: dict, page_number: int = 1) -> dict:
    from mission_of_words.brand import SERIES_LINE, TITLE

    plan = plan_header(
        c,
        page_number,
        kicker=SERIES_LINE,
        title=TITLE,
        reference=str(book.get("subtitle") or ""),
        instruction="A Christian fall activity book for kids ages 5-8.",
        header_fraction=0.28,
        instruction_fraction=0.0,
        instruction_in_header=True,
    )
    depth_bands(
        c,
        plan.art_box,
        (
            "CAST WAVE  ·  Mira, Eli, Joy, Caleb, Pip",
            "CHURCH FALL FESTIVAL  ·  lanterns, leaves, no letters in the art",
            "TITLE PLATE ART  ·  70%+ illustration  ·  children's book, not a worksheet",
        ),
    )
    return _record(page_number, "title", None, None, plan, ["title_lockup"], child_instruction="", asset_integration="Title plate: illustration owns the page.")


def draw_welcome_page(c: canvas.Canvas, book: dict, page_number: int = 2) -> dict:
    from mission_of_words.brand import WELCOME_HEADING

    plan = plan_header(
        c,
        page_number,
        kicker="How to use this book",
        title=WELCOME_HEADING,
        instruction="Read this page with a grown-up, then start Mission 1.",
        header_fraction=0.22,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    steps = [
        "Look at the mission map.",
        "Color the big picture.",
        "Find all 8 hidden gifts.",
        "Follow the path.",
        "Check, draw, and pray.",
    ]
    width = right - left
    col_w = width / 5
    for index, step in enumerate(steps):
        x = left + index * col_w + 4
        hatch_slot(c, (x, bottom + 40, x + col_w - 8, top - 8), f"{index + 1}")
        ink_text(c)
        c.setFont(BODY, 11)
        lines, _ = wrap_lines(c, step, BODY, 11, col_w - 12)
        y = bottom + 24
        for line in lines:
            c.drawString(x, y, line)
            y -= 13
    return _record(
        page_number,
        "welcome",
        None,
        None,
        plan,
        ["welcome_spot"],
        child_instruction="Read how to use the book, then start Mission 1 with a grown-up.",
        asset_integration="Welcome is a pictured how-to, not an onboarding wireframe.",
    )


def draw_contents_page(c: canvas.Canvas, missions: list[dict], page_number: int = 3) -> dict:
    plan = plan_header(
        c,
        page_number,
        kicker="Eight unique missions",
        title="Fall Faith Missions Map",
        instruction="Follow the winding path. Each stop is a different place.",
        header_fraction=0.18,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    hatch_slot(c, plan.art_box, "WINDING AUTUMN PATH  ·  eight unique environments")
    ink_text(c)
    y = top - 24
    for mission in missions:
        recipe = mission_recipe(mission["id"])
        line = f"p.{mission['global_page_start']}  {mission['title']}  ·  {recipe['environment']}"
        c.setFont(BODY_BOLD, 12)
        c.drawString(left + 12, y, line[:78])
        y -= 28
    return _record(
        page_number,
        "contents",
        None,
        None,
        plan,
        ["missions_map"],
        child_instruction="Find your mission on the map, then turn to that page.",
        asset_integration="Contents is a winding mission map, not a syllabus list.",
    )


def draw_parent_note_page(c: canvas.Canvas, book: dict, page_number: int = 4) -> dict:
    plan = plan_header(
        c,
        page_number,
        kicker="For parents and caregivers",
        title="A Note for Grown-ups",
        instruction="Little Lampkeepers is Bible-first. Each mission is locked to one public-domain verse.",
        header_fraction=0.22,
        instruction_in_header=True,
    )
    hatch_slot(c, (plan.art_box[0], plan.art_box[1], plan.art_box[2], plan.art_box[1] + 90), "LANTERN / LEAF MOTIF")
    left, bottom, right, top = plan.art_box
    note = (
        "Each mission is locked to one 1769 Oxford King James verse. Short quotations appear as source_text. "
        "The child paraphrase is labeled and is never mixed into the Bible wording. "
        "Activities help ages 5-8 practice the verse. They do not add extra Bible stories. "
        "Answer keys are in the back. This file is an INTERNAL geometry mock, not a KDP product."
    )
    ink_text(c)
    y = top - 8
    lines, overflow = wrap_lines(c, note, BODY, USED_INSTRUCTION_PT, right - left)
    plan.state.overflow.extend(overflow)
    for line in lines:
        c.setFont(BODY, USED_INSTRUCTION_PT)
        c.drawString(left, y - USED_INSTRUCTION_PT, line)
        y -= USED_INSTRUCTION_LEADING
    return _record(
        page_number,
        "parent_note",
        None,
        None,
        plan,
        ["parent_letter"],
        child_instruction="",
        asset_integration="Parent note is stationery, not a terms worksheet.",
    )


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
    recipe = mission_recipe(mission["id"])
    page = mission["pages"][1]
    plan = plan_header(
        c,
        page_number,
        kicker=f"Mission {mission['sequence']}  ·  Answer Key",
        title=str(mission.get("title") or ""),
        reference=str(canon.get("reference") or ""),
        instruction="Numbers match the Search & Find. The dark line is the unique maze path.",
        header_fraction=0.12,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    width = right - left
    height = top - bottom
    list_w = min(168, width * 0.28)
    search_h = height * 0.54
    search_box = (left, top - search_h, right - list_w - 8, top)
    list_box = (right - list_w, top - search_h, right, top)
    maze_box = (left, bottom, right, top - search_h - 16)

    hatch_slot(c, search_box, "SEARCH ANSWERS")
    raster_meta: dict = {}
    if search_composed and Path(search_composed).is_file():
        scene_w = search_box[2] - search_box[0]
        scene_h = search_box[3] - search_box[1]
        c.drawImage(
            ImageReader(str(search_composed)),
            search_box[0],
            search_box[1],
            width=scene_w,
            height=scene_h,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        with Image.open(search_composed) as image:
            img_w, img_h = image.size
        scale = min(scene_w / img_w, scene_h / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        ox = search_box[0] + (scene_w - draw_w) / 2
        oy = search_box[1] + (scene_h - draw_h) / 2
        for index, row in enumerate(search_manifest, start=1):
            cx = ox + (row["x"] + row["width"] / 2) * scale
            cy = oy + (img_h - (row["y"] + row["height"] / 2)) * scale
            radius = max(11.0, max(row["width"], row["height"]) * scale * 0.5)
            _callout(c, cx, cy, radius, index)
        raster_meta = {
            "raster_pixel_size": [img_w, img_h],
            "placed_points": [draw_w, draw_h],
            "effective_dpi": min(img_w / (draw_w / 72.0), img_h / (draw_h / 72.0)) if draw_w and draw_h else 0,
        }

    c.setFillColor(BAND)
    c.rect(list_box[0], list_box[1], list_box[2] - list_box[0], list_box[3] - list_box[1], fill=1, stroke=1)
    ink_text(c)
    c.setFont(BODY_BOLD, 11)
    c.drawString(list_box[0] + 6, list_box[3] - 14, "Find")
    for index, row in enumerate(search_manifest, start=1):
        c.setFont(BODY, 11)
        c.drawString(list_box[0] + 6, list_box[3] - 16 - index * 14, f"{index}. {display_name(row['name'])}")

    meta = draw_environment_maze(
        c,
        maze,
        maze_box,
        environment_kind=str(recipe["maze"]["environment_kind"]),
        answer_key=True,
    )
    ink_text(c)
    c.setFont(BODY_BOLD, 11)
    c.drawString(left, maze_box[3] + 4, "Maze path")
    names = [row["name"] for row in search_manifest]
    meta.pop("path", None)
    meta.pop("environment_kind", None)
    return _record(
        page_number,
        "answer_key",
        mission,
        page,
        plan,
        ["search_background", *names, "start_label", "finish_label"],
        search_manifest=search_manifest,
        maze_path=[list(cell) for cell in maze.solve()],
        environment_kind=recipe["maze"]["environment_kind"],
        asset_integration="Answer key uses the same search manifest and maze generator path. Callouts are print-scale.",
        **meta,
        **raster_meta,
    )


def draw_gratitude_page(c: canvas.Canvas, page_number: int = 45) -> dict:
    plan = plan_header(
        c,
        page_number,
        kicker="Bonus",
        title="A Thank-You Leaf Journal",
        instruction="Draw or write three things you thank God for.",
        header_fraction=0.16,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    h = (top - bottom - 16) / 3
    for index in range(3):
        y1 = top - index * (h + 8)
        hatch_slot(c, (left, y1 - h, right, y1), f"LEAF {index + 1}  ·  draw or write")
    return _record(
        page_number,
        "bonus_activity",
        None,
        None,
        plan,
        ["bonus_activity"],
        child_instruction="Draw or write three things you thank God for.",
        drawing_area_sqin=((right - left) / 72.0) * (h / 72.0) * 3,
        asset_integration="Three leaf journals, not a copied faith page.",
    )


def draw_prayer_walk_page(c: canvas.Canvas, page_number: int = 46) -> dict:
    plan = plan_header(
        c,
        page_number,
        kicker="Bonus",
        title="A Prayer Walk Together",
        instruction="Walk outside with a grown-up. Notice what God made. Then pray.",
        header_fraction=0.16,
        instruction_in_header=True,
    )
    left, bottom, right, top = plan.art_box
    hatch_slot(c, plan.art_box, "TRAIL WITH FOUR NOTICE STOPS")
    ink_text(c)
    c.setFont(PRAYER, 16)
    c.drawString(left + 12, bottom + 24, "God, thank You for making a world that is very good.")
    return _record(
        page_number,
        "bonus_activity",
        None,
        None,
        plan,
        ["bonus_activity"],
        child_instruction="Walk outside with a grown-up. Notice four things God made, then pray.",
        asset_integration="Outdoor noticing trail, unique from the gratitude journal.",
    )


def draw_certificate_page(c: canvas.Canvas, book: dict, page_number: int = 47) -> dict:
    from mission_of_words.brand import CERTIFICATE_HEADING, CERTIFICATE_LINE

    plan = plan_header(
        c,
        page_number,
        kicker="You did it",
        title=CERTIFICATE_HEADING,
        instruction="Write your name and the date on the certificate.",
        header_fraction=0.20,
        instruction_in_header=True,
    )
    hatch_slot(c, plan.art_box, "LANTERN SEAL  ·  CAST CONFETTI  ·  NO LETTERS IN ART")
    left, bottom, right, _top = plan.art_box
    ink_text(c)
    c.setFont(BODY, USED_INSTRUCTION_PT)
    c.drawCentredString((left + right) / 2, bottom + 36, CERTIFICATE_LINE)
    return _record(
        page_number,
        "certificate",
        None,
        None,
        plan,
        ["certificate_frame"],
        child_instruction="Write your name and the date on the certificate.",
        asset_integration="Certificate with lantern seal, not a generic award box.",
    )


def draw_closing_page(c: canvas.Canvas, book: dict, page_number: int = 48) -> dict:
    from mission_of_words.brand import CLOSING_HEADING, TITLE

    plan = plan_header(
        c,
        page_number,
        kicker="Keep going",
        title=CLOSING_HEADING,
        instruction="Remember one way you can shine God's light this week.",
        header_fraction=0.20,
        instruction_in_header=True,
    )
    depth_bands(
        c,
        plan.art_box,
        (
            "CAST WALKING HOME WITH LANTERNS",
            TITLE,
            "Go do one good thing today.",
        ),
    )
    return _record(
        page_number,
        "closing",
        None,
        None,
        plan,
        ["closing_lockup"],
        child_instruction="Remember one way you can shine God's light this week.",
        asset_integration="Closing lockup is distinct from the title page.",
    )


# Backward-compatible names used by older tests.
def measure_activity_header(page_number: int, **kwargs) -> HeaderPlan:
    title = str(kwargs.get("mission_title") or kwargs.get("activity_title") or "")
    kicker = "MISSION"
    if kwargs.get("mission_number") is not None:
        kicker = f"Mission {kwargs['mission_number']}"
        if kwargs.get("activity_label"):
            kicker = f"{kicker}  ·  {kwargs['activity_label']}"
    return measure_header(
        page_number,
        kicker=kicker,
        title=title,
        reference=str(kwargs.get("reference") or ""),
        instruction=str(kwargs.get("instruction") or ""),
        header_fraction=0.16 if kwargs.get("hero") else 0.14,
        instruction_fraction=0.10 if kwargs.get("hero") else 0.0,
        instruction_in_header=not kwargs.get("hero"),
        box=kwargs.get("box"),
    )


def draw_activity_header(c: canvas.Canvas, page_number: int, **kwargs) -> HeaderPlan:
    title = str(kwargs.get("mission_title") or kwargs.get("activity_title") or "")
    kicker = "MISSION"
    if kwargs.get("mission_number") is not None:
        kicker = f"Mission {kwargs['mission_number']}"
        if kwargs.get("activity_label"):
            kicker = f"{kicker}  ·  {kwargs['activity_label']}"
    return plan_header(
        c,
        page_number,
        kicker=kicker,
        title=title,
        reference=str(kwargs.get("reference") or ""),
        instruction=str(kwargs.get("instruction") or ""),
        header_fraction=0.16 if kwargs.get("hero") else 0.14,
        instruction_fraction=0.10 if kwargs.get("hero") else 0.0,
        instruction_in_header=not kwargs.get("hero"),
        box=kwargs.get("box"),
    )
