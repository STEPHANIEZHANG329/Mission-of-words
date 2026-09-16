"""Compose the 48-page interior PDF. Vector type + placed GPT2 artwork."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, black, white
from reportlab.pdfgen import canvas

from llk.fonts import (
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SANS_ITALIC,
    FONT_SANS_SEMI,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    FONT_TITLE,
    register_fonts,
)
from llk.geometry import TRIM_H, TRIM_W, margins_for_page, pt
from llk.images import crop_sheet_cell, find_art, fit_rect, largest_white_rect, open_lineart, prepare_for_pdf
from llk.layout import Box, assert_no_collisions
from llk.maze import Maze, generate_maze, wall_segments
from llk.paths import OUTPUT, ensure_dirs
from llk.search_place import place_targets
from llk.spec import BookSpec, Mission, load_spec, target_catalog

INK = Color(0.07, 0.07, 0.08)
RULE = Color(0.15, 0.15, 0.16)
LIGHT = Color(0.72, 0.72, 0.73)
PALE = Color(0.92, 0.92, 0.93)
ACCENT = Color(0.18, 0.18, 0.2)


def _wrap(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        if c.stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    font: str,
    size: float,
    max_width: float,
    leading: float | None = None,
    fill=INK,
) -> float:
    leading = leading or size * 1.28
    c.setFillColor(fill)
    c.setFont(font, size)
    for line in _wrap(c, text, font, size, max_width):
        c.drawString(x, y, line)
        y -= leading
    return y


class Composer:
    def __init__(self, spec: BookSpec | None = None):
        self.spec = spec or load_spec()
        self.catalog = target_catalog(self.spec.missions)
        self.missions = {m.id: m for m in self.spec.missions}
        self.mazes: dict[str, Maze] = {}
        for mission in self.spec.missions:
            maze_page = mission.pages[2]
            cols, rows = maze_page.maze_grid
            self.mazes[mission.id] = generate_maze(cols, rows, maze_page.maze_seed)
        self._img_cache: dict[str, str] = {}
        self._boxes: list[Box] = []

    def mission(self, page: dict) -> Mission:
        return self.missions[page["mission_id"]]

    def _tmp_image(self, img: Image.Image, name: str) -> str:
        ensure_dirs()
        path = OUTPUT / "_pages" / f"{name}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        prepare_for_pdf(img).save(path, "JPEG", quality=90, optimize=True)
        return str(path)

    def draw_image(self, c: canvas.Canvas, asset_id: str, x: float, y: float, w: float, h: float) -> Box:
        img = open_lineart(asset_id, color=asset_id == "cover_front")
        dx, dy, nw, nh = fit_rect(img.size[0], img.size[1], x, y, w, h)
        path = self._tmp_image(img, f"placed_{asset_id}_{int(dx)}_{int(dy)}_{int(nw)}")
        c.drawImage(path, dx, dy, nw, nh, preserveAspectRatio=True, mask="auto")
        box = Box(f"art:{asset_id}", dx, dy, nw, nh)
        self._boxes.append(box)
        return box

    def footer(self, c: canvas.Canvas, page_number: int) -> None:
        m = margins_for_page(page_number)
        c.setFillColor(INK)
        c.setFont(FONT_SANS, 9)
        label = str(page_number)
        c.drawCentredString(pt(TRIM_W) / 2, pt(m.bottom) - 18, label)
        c.setFont(FONT_SANS, 8)
        c.setFillColor(RULE)
        c.drawString(pt(m.left), pt(m.bottom) - 18, "Little Lampkeepers")

    def header_block(
        self,
        c: canvas.Canvas,
        page: dict,
        *,
        kicker: str,
        title: str,
        instruction: str = "",
        verse: str = "",
        paraphrase: str = "",
    ) -> float:
        m = margins_for_page(page["page"])
        x = pt(m.left)
        width = pt(m.content_width)
        top = pt(TRIM_H - m.top) - 4
        y = top
        c.setFillColor(ACCENT)
        c.setFont(FONT_SANS_SEMI, 10)
        c.drawString(x, y, kicker.upper())
        y -= 22
        c.setFillColor(INK)
        c.setFont(FONT_TITLE, 18)
        for line in _wrap(c, title, FONT_TITLE, 18, width):
            c.drawString(x, y, line)
            y -= 22
        if verse:
            y -= 2
            c.setFont(FONT_SERIF_BOLD, 12)
            c.setFillColor(INK)
            c.drawString(x, y, verse)
            y -= 16
        if paraphrase:
            y = _draw_wrapped(c, paraphrase, x, y, FONT_SERIF, 12, width, 16) - 4
        if instruction:
            y = _draw_wrapped(c, instruction, x, y, FONT_SANS, 12, width, 16)
        y -= 10
        c.setStrokeColor(LIGHT)
        c.setLineWidth(1)
        c.line(x, y, x + width, y)
        self._boxes.append(Box("rule:header", x, y - 1, width, 2))
        self._boxes.append(Box("text:header", x, y + 8, width, top - (y + 8)))
        y -= 14
        return y

    def page_title(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(1)
        art_h = pt(6.15)
        self.draw_image(
            c,
            "title_scene",
            pt(m.left),
            pt(TRIM_H - m.top) - art_h,
            pt(m.content_width),
            art_h,
        )
        y = pt(TRIM_H - m.top) - art_h - 22
        y = _draw_wrapped(
            c, meta["title"], pt(m.left), y, FONT_TITLE, 20, pt(m.content_width), 24
        )
        y = _draw_wrapped(
            c, meta["subtitle"], pt(m.left), y - 2, FONT_SANS_SEMI, 12, pt(m.content_width), 16
        )
        y = _draw_wrapped(
            c, meta["tagline"], pt(m.left), y, FONT_SANS, 12, pt(m.content_width), 15
        )
        y = _draw_wrapped(
            c, meta["author_line"], pt(m.left), y - 4, FONT_SANS_ITALIC, 11, pt(m.content_width), 14
        )
        _draw_wrapped(
            c, meta["ownership"], pt(m.left), y - 8, FONT_SANS, 9, pt(m.content_width), 12
        )

    def page_welcome(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(2)
        y = self.header_block(c, page, kicker="How to use this book", title=meta["welcome_title"])
        art_h = pt(3.15)
        self.draw_image(c, "welcome_cast", pt(m.left), y - art_h - 8, pt(m.content_width), art_h)
        y = y - art_h - 22
        for para in meta["welcome_body"]:
            y = _draw_wrapped(c, para, pt(m.left), y, FONT_SANS, 12, pt(m.content_width), 16) - 6
        y -= 6
        c.setFont(FONT_SANS_BOLD, 12)
        c.setFillColor(INK)
        c.drawString(pt(m.left), y, "On every mission you will:")
        y -= 18
        for item in meta["how_to_use"]:
            y = _draw_wrapped(c, "• " + item, pt(m.left), y, FONT_SANS, 12, pt(m.content_width), 16) - 2

    def page_contents(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(3)
        y = self.header_block(c, page, kicker="Eight missions", title=meta["map_title"], instruction=meta["map_intro"])
        art_h = pt(4.2)
        self.draw_image(c, "missions_map", pt(m.left), y - art_h - 6, pt(m.content_width), art_h)
        y = y - art_h - 20
        for mission in self.spec.missions:
            start = mission.global_page_start
            line = f"{mission.sequence}. {mission.title}  ·  {mission.scripture_reference}  ·  pp. {start}–{start+3}"
            y = _draw_wrapped(c, line, pt(m.left), y, FONT_SANS, 12, pt(m.content_width), 16) - 2

    def page_parent(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(4)
        y = self.header_block(c, page, kicker="For grown-ups", title=meta["parent_title"])
        art_h = pt(2.4)
        self.draw_image(c, "parent_spot", pt(m.left), y - art_h - 4, pt(m.content_width), art_h)
        y = y - art_h - 18
        for para in meta["parent_body"]:
            y = _draw_wrapped(c, para, pt(m.left), y, FONT_SANS, 12, pt(m.content_width), 16) - 8

    def page_coloring(self, c: canvas.Canvas, page: dict) -> None:
        mission = self.mission(page)
        coloring = mission.pages[0]
        canon = self.spec.canon[mission.canon_id]
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker=f"Mission {mission.sequence}  ·  Color",
            title=coloring.title,
            instruction=coloring.instruction,
            verse=canon.reference,
            paraphrase=canon.child_paraphrase,
        )
        bottom = pt(m.bottom) + 8
        self.draw_image(c, page["art"], pt(m.left), bottom, pt(m.content_width), y - 10 - bottom)

    def page_search(self, c: canvas.Canvas, page: dict) -> None:
        mission = self.mission(page)
        search = mission.pages[1]
        canon = self.spec.canon[mission.canon_id]
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker=f"Mission {mission.sequence}  ·  Search & Find",
            title=search.title,
            instruction=search.instruction,
            verse=canon.reference,
        )
        names = [t.name.replace("_", " ") for t in search.targets]
        col_w = pt(m.content_width) / 2
        c.setFont(FONT_SANS, 12)
        c.setFillColor(INK)
        for i, name in enumerate(names):
            col = i % 2
            row = i // 2
            c.drawString(pt(m.left) + col * col_w, y - row * 16, f"☐  {name}")
        y -= 16 * 4 + 12
        bottom = pt(m.bottom) + 8
        box_x, box_y = pt(m.left), bottom
        box_w, box_h = pt(m.content_width), y - bottom
        self._draw_search_scene(c, mission, box_x, box_y, box_w, box_h)

    def _fitted_search_rect(self, mission: Mission, x: float, y: float, w: float, h: float) -> Box:
        bg = open_lineart(f"search_bg_{mission.id}")
        dx, dy, nw, nh = fit_rect(bg.size[0], bg.size[1], x, y, w, h)
        return Box(f"art:search_bg_{mission.id}", dx, dy, nw, nh)

    def _draw_search_scene(
        self, c: canvas.Canvas, mission: Mission, x: float, y: float, w: float, h: float
    ) -> list[Box]:
        bg_id = f"search_bg_{mission.id}"
        art_box = self.draw_image(c, bg_id, x, y, w, h)
        bg = open_lineart(bg_id)
        search = mission.pages[1]
        placements = place_targets(bg, search.targets)
        sheet_cache: dict[str, Image.Image] = {}
        drawn = []
        for placed in placements:
            sheet_id, col, row = self.catalog[placed.name]
            if sheet_id not in sheet_cache:
                sheet_cache[sheet_id] = Image.open(find_art(sheet_id)).convert("RGB")
            cell = crop_sheet_cell(sheet_cache[sheet_id], col, row)
            tw = art_box.w * placed.scale
            th = tw * (cell.size[1] / max(cell.size[0], 1))
            tx = art_box.x + art_box.w * placed.x
            ty = art_box.y + art_box.h * (1 - placed.y) - th
            tx = min(max(tx, art_box.x), art_box.x + art_box.w - tw)
            ty = min(max(ty, art_box.y), art_box.y + art_box.h - th)
            tmp = OUTPUT / "_pages" / f"tgt_{mission.id}_{placed.name}.png"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            cell.save(tmp, "PNG")
            c.drawImage(str(tmp), tx, ty, tw, th, mask="auto")
            drawn.append(Box(f"target:{placed.name}", tx, ty, tw, th))
        return drawn

    def page_maze(self, c: canvas.Canvas, page: dict) -> None:
        mission = self.mission(page)
        maze_page = mission.pages[2]
        canon = self.spec.canon[mission.canon_id]
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker=f"Mission {mission.sequence}  ·  Maze",
            title=maze_page.title,
            instruction=maze_page.instruction,
            verse=canon.reference,
        )
        maze = self.mazes[mission.id]
        bottom = pt(m.bottom) + 30
        self._draw_maze_vector(
            c,
            maze,
            pt(m.left),
            bottom,
            pt(m.content_width),
            y - 6 - bottom,
            start_label=maze_page.start_label,
            finish_label=maze_page.finish_label,
        )

    def _draw_maze_vector(
        self,
        c: canvas.Canvas,
        maze: Maze,
        x: float,
        y: float,
        w: float,
        h: float,
        start_label: str,
        finish_label: str,
        solution: bool = False,
    ) -> None:
        pad_x, pad_top, pad_bot = 10, 22, 22
        inner_w, inner_h = w - pad_x * 2, h - pad_top - pad_bot
        cell_w = inner_w / maze.cols
        cell_h = inner_h / maze.rows
        origin_x = x + pad_x
        origin_y = y + pad_bot
        c.setStrokeColor(INK)
        c.setLineWidth(2.6)
        c.setLineCap(0)
        c.setLineJoin(0)
        for x1, y1, x2, y2 in wall_segments(maze):
            # cell units, y downward from top of maze -> reportlab y upward from origin_y
            ax = origin_x + x1 * cell_w
            ay = origin_y + (maze.rows - y1) * cell_h
            bx = origin_x + x2 * cell_w
            by = origin_y + (maze.rows - y2) * cell_h
            c.line(ax, ay, bx, by)
        if solution:
            c.setStrokeColor(Color(0.35, 0.35, 0.36))
            c.setLineWidth(2.0)
            pts = []
            for col, row in maze.path:
                px = origin_x + (col + 0.5) * cell_w
                py = origin_y + (maze.rows - 1 - row + 0.5) * cell_h
                pts.append((px, py))
            p = c.beginPath()
            p.moveTo(pts[0][0], pts[0][1])
            for px, py in pts[1:]:
                p.lineTo(px, py)
            c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont(FONT_SANS_BOLD, 12)
        c.drawString(origin_x, origin_y + maze.rows * cell_h + 6, start_label)
        c.drawRightString(origin_x + maze.cols * cell_w, origin_y - 14, finish_label)

    def page_faith(self, c: canvas.Canvas, page: dict) -> None:
        mission = self.mission(page)
        faith = mission.pages[3]
        canon = self.spec.canon[mission.canon_id]
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker=f"Mission {mission.sequence}  ·  Faith in Action",
            title=faith.title,
            instruction=faith.instruction,
            verse=canon.reference,
            paraphrase=canon.child_paraphrase,
        )
        banner_h = pt(2.05)
        self.draw_image(c, page["art"], pt(m.left), y - banner_h - 4, pt(m.content_width), banner_h)
        y = y - banner_h - 20
        for choice in faith.choices:
            self._checkbox(c, pt(m.left), y, choice["label"])
            y -= 22
        y -= 8
        c.setFont(FONT_SANS_SEMI, 12)
        c.setFillColor(INK)
        c.drawString(pt(m.left), y, faith.drawing_prompt)
        y -= 10
        box_h = y - pt(m.bottom) - 48
        c.setStrokeColor(INK)
        c.setLineWidth(1.5)
        c.roundRect(pt(m.left), pt(m.bottom) + 36, pt(m.content_width), box_h, 8, stroke=1, fill=0)
        c.setFillColor(INK)
        _draw_wrapped(
            c,
            "Prayer: " + faith.prayer,
            pt(m.left),
            pt(m.bottom) + 16,
            FONT_SERIF,
            12,
            pt(m.content_width),
            14,
        )

    def _checkbox(self, c: canvas.Canvas, x: float, y: float, label: str) -> None:
        c.setStrokeColor(INK)
        c.setLineWidth(1.4)
        c.rect(x, y - 1, 12, 12, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont(FONT_SANS, 12)
        c.drawString(x + 18, y, label)

    def page_answer(self, c: canvas.Canvas, page: dict) -> None:
        mission = self.mission(page)
        search = mission.pages[1]
        maze_page = mission.pages[2]
        canon = self.spec.canon[mission.canon_id]
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker=f"Answer Key  ·  Mission {mission.sequence}",
            title=page["title"],
            verse=canon.reference,
        )
        c.setFont(FONT_SANS_BOLD, 12)
        c.setFillColor(INK)
        c.drawString(pt(m.left), y, f"Search & Find · page {mission.global_page_start + 1}")
        y -= 16
        names = [f"{i+1}. {t.name.replace('_', ' ')}" for i, t in enumerate(search.targets)]
        col_w = pt(m.content_width) / 2
        c.setFont(FONT_SANS, 11)
        for i, name in enumerate(names):
            c.drawString(pt(m.left) + (i % 2) * col_w, y - (i // 2) * 14, name)
        y -= 14 * 4 + 8
        # Portrait preview box so contain-fit is large and never stretched.
        map_w = pt(2.85)
        map_h = pt(4.15)
        map_x = pt(m.left) + (pt(m.content_width) - map_w) / 2
        map_y = y - map_h
        c.setStrokeColor(INK)
        c.setLineWidth(1)
        c.rect(map_x, map_y, map_w, map_h, stroke=1, fill=0)
        bg_id = f"search_bg_{mission.id}"
        art_box = self.draw_image(c, bg_id, map_x + 3, map_y + 3, map_w - 6, map_h - 6)
        placements = place_targets(open_lineart(bg_id), search.targets)
        for i, placed in enumerate(placements, start=1):
            cx = art_box.x + placed.x * art_box.w + (placed.scale * art_box.w) / 2
            cy = art_box.y + (1 - placed.y) * art_box.h - (placed.scale * art_box.w) / 2
            c.setFillColor(white)
            c.setStrokeColor(INK)
            c.circle(cx, cy, 8, stroke=1, fill=1)
            c.setFillColor(INK)
            c.setFont(FONT_SANS_BOLD, 9)
            c.drawCentredString(cx, cy - 3, str(i))
        y = map_y - 18
        c.setFillColor(INK)
        c.setFont(FONT_SANS_BOLD, 12)
        c.drawString(pt(m.left), y, f"Maze · page {mission.global_page_start + 2}  ·  unique path")
        y -= 8
        maze = self.mazes[mission.id]
        self._draw_maze_vector(
            c,
            maze,
            pt(m.left),
            pt(m.bottom) + 8,
            pt(m.content_width),
            y - 10 - (pt(m.bottom) + 8),
            start_label=maze_page.start_label,
            finish_label=maze_page.finish_label,
            solution=True,
        )

    def page_gratitude(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker="Bonus with a grown-up",
            title=meta["gratitude_title"],
            instruction=meta["gratitude_intro"],
        )
        art_h = pt(2.4)
        self.draw_image(c, "gratitude_spot", pt(m.left), y - art_h, pt(m.content_width), art_h)
        y = y - art_h - 18
        prompts = [
            "1. I thank God for…",
            "2. I thank God for…",
            "3. I thank God for…",
        ]
        for prompt in prompts:
            c.setFont(FONT_SANS_SEMI, 12)
            c.setFillColor(INK)
            c.drawString(pt(m.left), y, prompt)
            y -= 8
            for _ in range(3):
                c.setStrokeColor(LIGHT)
                c.line(pt(m.left), y, pt(m.left + m.content_width), y)
                y -= 18
            y -= 10
        c.setFont(FONT_SANS, 12)
        c.drawString(pt(m.left), y, "Draw one of those three thanks in the box.")
        y -= 8
        c.setStrokeColor(INK)
        c.roundRect(pt(m.left), pt(m.bottom) + 8, pt(m.content_width), y - 6 - (pt(m.bottom) + 8), 8, 1, 0)

    def page_prayer_walk(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(page["page"])
        y = self.header_block(
            c,
            page,
            kicker="Bonus with a grown-up",
            title=meta["prayer_walk_title"],
            instruction=meta["prayer_walk_intro"],
        )
        boxes = [
            "I saw…",
            "I heard…",
            "A person I can pray for…",
            "A short thank-you prayer…",
        ]
        box_h = (y - pt(m.bottom) - 20) / 4 - 10
        for label in boxes:
            c.setFont(FONT_SANS_SEMI, 12)
            c.setFillColor(INK)
            c.drawString(pt(m.left), y, label)
            y -= 8
            c.setStrokeColor(INK)
            c.roundRect(pt(m.left), y - box_h, pt(m.content_width), box_h, 6, 1, 0)
            y = y - box_h - 14

    def page_certificate(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(page["page"])
        art_box = self.draw_image(
            c,
            "certificate_frame",
            pt(m.left),
            pt(m.bottom),
            pt(m.content_width),
            pt(m.content_height),
        )
        img = open_lineart("certificate_frame")
        nx, ny, nw, nh = largest_white_rect(img)
        # Image-space y is top-origin; reportlab y is bottom-origin.
        field_x = art_box.x + nx * art_box.w + 6
        field_w = max(120, nw * art_box.w - 12)
        field_top = art_box.y + art_box.h - ny * art_box.h - 4
        field_h = nh * art_box.h - 8
        field_bottom = field_top - field_h
        y = field_top - 2
        c.setFillColor(INK)
        c.setFont(FONT_TITLE, 14)
        for line in _wrap(c, meta["certificate_title"], FONT_TITLE, 14, field_w):
            c.drawCentredString(field_x + field_w / 2, y, line)
            y -= 16
        c.setFont(FONT_SANS, 11)
        c.drawCentredString(field_x + field_w / 2, y, "This certifies that")
        y -= 16
        c.setStrokeColor(INK)
        c.line(field_x + 6, y, field_x + field_w - 6, y)
        c.setFont(FONT_SANS, 8)
        c.drawCentredString(field_x + field_w / 2, y - 10, "name")
        y -= 22
        y = _draw_wrapped(
            c,
            meta["certificate_body"],
            field_x,
            y,
            FONT_SANS,
            11,
            field_w,
            13,
        )
        y -= 12
        mid = field_x + field_w / 2
        c.line(field_x + 2, y, mid - 8, y)
        c.line(mid + 8, y, field_x + field_w - 2, y)
        c.setFont(FONT_SANS, 8)
        c.drawCentredString((field_x + 2 + mid - 8) / 2, y - 10, "grown-up signature")
        c.drawCentredString((mid + 8 + field_x + field_w - 2) / 2, y - 10, "date")
        if y - 10 < field_bottom + 2:
            raise AssertionError("certificate type escaped the clear center field")

    def page_closing(self, c: canvas.Canvas, page: dict) -> None:
        meta = self.spec.meta
        m = margins_for_page(page["page"])
        y = self.header_block(c, page, kicker="Until next season", title=meta["closing_title"])
        art_h = pt(6.2)
        self.draw_image(c, "closing_scene", pt(m.left), y - art_h - 8, pt(m.content_width), art_h)
        y = y - art_h - 22
        _draw_wrapped(c, meta["closing_body"], pt(m.left), y, FONT_SANS, 12, pt(m.content_width), 16)

    def draw_page(self, c: canvas.Canvas, page: dict) -> None:
        kind = page["type"]
        dispatch = {
            "title": self.page_title,
            "welcome": self.page_welcome,
            "contents": self.page_contents,
            "parent_note": self.page_parent,
            "coloring": self.page_coloring,
            "search_find": self.page_search,
            "maze": self.page_maze,
            "faith_interaction": self.page_faith,
            "answer_key": self.page_answer,
            "bonus_gratitude": self.page_gratitude,
            "bonus_prayer_walk": self.page_prayer_walk,
            "certificate": self.page_certificate,
            "closing": self.page_closing,
        }
        dispatch[kind](c, page)
        self.footer(c, page["page"])

    def write_interior(self, dest: Path | None = None) -> Path:
        register_fonts()
        ensure_dirs()
        dest = dest or (OUTPUT / "LittleLampkeepers_48Page_Interior_KDP.pdf")
        c = canvas.Canvas(str(dest), pagesize=(pt(TRIM_W), pt(TRIM_H)))
        c.setTitle(self.spec.meta["title"])
        c.setAuthor("Little Lampkeepers")
        c.setSubject("Christian fall activity book interior, 48 pages, 8.5x11")
        for page in self.spec.pages:
            self._boxes = []
            self.draw_page(c, page)
            assert_no_collisions(self._boxes)
            c.showPage()
        c.save()
        return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)
    dest = Path(args.out) if args.out else None
    path = Composer().write_interior(dest)
    print(f"WROTE {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
