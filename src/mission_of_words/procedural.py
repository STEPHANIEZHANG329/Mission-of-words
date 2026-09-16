"""Unpaid procedural line-art rasters for Search & Find.

These files stand in for later model-drawn accepted assets. Code still owns
placement, counts, and the answer key. No image API is called.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from mission_of_words.layout import DPI

TARGET_CANVAS = 512
STROKE = 14
BLACK = (0, 0, 0, 255)
CLEAR = (0, 0, 0, 0)
WHITE = (255, 255, 255, 255)


def _new(size: int = TARGET_CANVAS) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (size, size), CLEAR)
    return image, ImageDraw.Draw(image)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_lantern(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    body = [x0 + w * 0.18, y0 + h * 0.28, x1 - w * 0.18, y1 - h * 0.12]
    draw.rounded_rectangle(body, radius=18, fill=WHITE, outline=BLACK, width=STROKE)
    draw.polygon(
        [
            (x0 + w * 0.22, y0 + h * 0.28),
            (x1 - w * 0.22, y0 + h * 0.28),
            (x1 - w * 0.32, y0 + h * 0.14),
            (x0 + w * 0.32, y0 + h * 0.14),
        ],
        fill=WHITE,
        outline=BLACK,
        width=STROKE,
    )
    draw.arc(
        [x0 + w * 0.28, y0 - h * 0.02, x1 - w * 0.28, y0 + h * 0.28],
        start=0,
        end=180,
        fill=BLACK,
        width=STROKE,
    )
    cx = (x0 + x1) / 2
    draw.line([(cx, body[1] + 12), (cx, body[3] - 12)], fill=BLACK, width=max(6, STROKE // 2))
    draw.polygon(
        [
            (cx, y0 + h * 0.42),
            (cx + w * 0.10, y0 + h * 0.62),
            (cx, y0 + h * 0.72),
            (cx - w * 0.10, y0 + h * 0.62),
        ],
        fill=WHITE,
        outline=BLACK,
        width=max(6, STROKE // 2),
    )


def draw_pumpkin(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.ellipse([x0 + 8, y0 + h * 0.22, x1 - 8, y1 - 8], fill=WHITE, outline=BLACK, width=STROKE)
    draw.arc(
        [x0 + w * 0.22, y0 + h * 0.28, x0 + w * 0.48, y1 - 16],
        start=250,
        end=110,
        fill=BLACK,
        width=max(6, STROKE // 2),
    )
    draw.arc(
        [x0 + w * 0.52, y0 + h * 0.28, x0 + w * 0.78, y1 - 16],
        start=250,
        end=110,
        fill=BLACK,
        width=max(6, STROKE // 2),
    )
    draw.rectangle(
        [x0 + w * 0.45, y0 + h * 0.08, x0 + w * 0.55, y0 + h * 0.28],
        fill=WHITE,
        outline=BLACK,
        width=max(6, STROKE // 2),
    )


def draw_apple(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.ellipse([x0 + 20, y0 + h * 0.18, x1 - 20, y1 - 12], fill=WHITE, outline=BLACK, width=STROKE)
    draw.line(
        [(x0 + w * 0.5, y0 + h * 0.22), (x0 + w * 0.58, y0 + h * 0.06)],
        fill=BLACK,
        width=STROKE,
    )
    draw.arc(
        [x0 + w * 0.32, y0 + h * 0.10, x0 + w * 0.68, y0 + h * 0.34],
        start=200,
        end=340,
        fill=BLACK,
        width=max(6, STROKE // 2),
    )


def draw_leaf(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.ellipse([x0 + w * 0.16, y0 + 20, x1 - w * 0.16, y1 - 40], fill=WHITE, outline=BLACK, width=STROKE)
    cx = (x0 + x1) / 2
    draw.line([(cx, y1 - 12), (cx, y0 + h * 0.55)], fill=BLACK, width=STROKE)
    draw.line([(cx, y0 + h * 0.45), (x0 + w * 0.28, y0 + h * 0.32)], fill=BLACK, width=max(6, STROKE // 2))
    draw.line([(cx, y0 + h * 0.45), (x1 - w * 0.28, y0 + h * 0.32)], fill=BLACK, width=max(6, STROKE // 2))


def draw_acorn(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.ellipse([x0 + w * 0.18, y0 + h * 0.32, x1 - w * 0.18, y1 - 12], fill=WHITE, outline=BLACK, width=STROKE)
    draw.polygon(
        [
            (x0 + w * 0.12, y0 + h * 0.42),
            (x1 - w * 0.12, y0 + h * 0.42),
            (x1 - w * 0.22, y0 + h * 0.18),
            (x0 + w * 0.22, y0 + h * 0.18),
        ],
        fill=WHITE,
        outline=BLACK,
        width=STROKE,
    )
    draw.line(
        [(x0 + w * 0.5, y0 + h * 0.18), (x0 + w * 0.5, y0 + 8)],
        fill=BLACK,
        width=STROKE,
    )


def draw_scarf(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.polygon(
        [
            (x0 + 16, y0 + h * 0.28),
            (x1 - 20, y0 + h * 0.42),
            (x1 - 28, y0 + h * 0.62),
            (x0 + 8, y0 + h * 0.48),
        ],
        fill=WHITE,
        outline=BLACK,
        width=STROKE,
    )
    draw.line(
        [(x0 + w * 0.18, y0 + h * 0.40), (x1 - w * 0.28, y0 + h * 0.52)],
        fill=BLACK,
        width=max(6, STROKE // 2),
    )
    draw.line(
        [(x0 + w * 0.22, y0 + h * 0.46), (x1 - w * 0.24, y0 + h * 0.58)],
        fill=BLACK,
        width=max(6, STROKE // 2),
    )
    for i in range(4):
        draw.line(
            [(x0 + 10 + i * 8, y0 + h * 0.48), (x0 + 4 + i * 8, y0 + h * 0.62)],
            fill=BLACK,
            width=max(6, STROKE // 2),
        )


def draw_bible(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rounded_rectangle(
        [x0 + 18, y0 + 28, x1 - 18, y1 - 18],
        radius=14,
        fill=WHITE,
        outline=BLACK,
        width=STROKE,
    )
    draw.rectangle(
        [x0 + 18, y0 + 28, x0 + w * 0.22, y1 - 18],
        outline=BLACK,
        width=max(6, STROKE // 2),
    )
    cx, cy = x0 + w * 0.60, y0 + h * 0.55
    draw.line([(cx, cy - 70), (cx, cy + 70)], fill=BLACK, width=STROKE + 2)
    draw.line([(cx - 40, cy - 18), (cx + 40, cy - 18)], fill=BLACK, width=STROKE + 2)


def draw_basket(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.polygon(
        [
            (x0 + w * 0.12, y0 + h * 0.48),
            (x1 - w * 0.12, y0 + h * 0.48),
            (x1 - w * 0.22, y1 - 16),
            (x0 + w * 0.22, y1 - 16),
        ],
        fill=WHITE,
        outline=BLACK,
        width=STROKE,
    )
    draw.arc(
        [x0 + w * 0.16, y0 + h * 0.08, x1 - w * 0.16, y0 + h * 0.70],
        start=0,
        end=180,
        fill=BLACK,
        width=STROKE,
    )
    draw.line(
        [(x0 + w * 0.22, y0 + h * 0.62), (x1 - w * 0.22, y0 + h * 0.62)],
        fill=BLACK,
        width=max(6, STROKE // 2),
    )


TARGET_DRAWERS = {
    "lantern": draw_lantern,
    "pumpkin": draw_pumpkin,
    "apple": draw_apple,
    "leaf": draw_leaf,
    "acorn": draw_acorn,
    "scarf": draw_scarf,
    "basket": draw_basket,
    "Bible": draw_bible,
}

TARGET_PROMPTS = {
    "lantern": "Black-and-white coloring-book lantern, closed shapes, handle and flame, no letters.",
    "pumpkin": "Black-and-white coloring-book pumpkin with stem and lobe lines, no face, no letters.",
    "apple": "Black-and-white coloring-book apple with stem, no letters.",
    "leaf": "Black-and-white coloring-book maple-style leaf, closed outline, no letters.",
    "acorn": "Black-and-white coloring-book acorn with cap, no letters.",
    "scarf": "Black-and-white coloring-book winter scarf with fringe, no letters.",
    "basket": "Black-and-white coloring-book picnic basket with handle, no letters.",
    "Bible": "Black-and-white coloring-book closed Bible with intact cross on cover, no letters.",
}


def render_target(name: str, path: Path, size: int = TARGET_CANVAS) -> dict:
    if name not in TARGET_DRAWERS:
        raise ValueError(f"unknown target: {name}")
    image, draw = _new(size)
    inset = int(size * 0.08)
    TARGET_DRAWERS[name](draw, (inset, inset, size - inset, size - inset))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return {
        "asset_id": f"proc_{name.lower()}",
        "role": "search_target",
        "status": "accepted",
        "request_id": f"procedural-{name}",
        "model": "procedural-lineart",
        "prompt": TARGET_PROMPTS[name],
        "file": str(path),
        "sha256": _sha256(path),
        "cost_usd": 0.0,
        "attempts": 1,
        "paid_call": False,
        "dpi": DPI,
    }


def render_search_background(path: Path, width: int, height: int) -> dict:
    """Festival grounds without the eight search targets."""
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    w, h = width, height
    stroke = max(8, round(min(w, h) / 180))

    def line_ink(xy, width_=stroke):
        draw.line(xy, fill=(0, 0, 0), width=width_)

    # ground
    ground_y = int(h * 0.72)
    draw.polygon(
        [(0, ground_y), (w, int(h * 0.70)), (w, h), (0, h)],
        fill=(255, 255, 255),
        outline=(0, 0, 0),
        width=stroke,
    )
    # church sits on the ground — path meets the door instead of cutting the building
    bx0, by0 = int(w * 0.18), int(h * 0.38)
    bx1, by1 = int(w * 0.48), ground_y
    draw.polygon(
        [
            (int(w * 0.40), h),
            (int(w * 0.60), h),
            (int(w * 0.52), by1),
            (int(w * 0.44), by1),
        ],
        outline=(0, 0, 0),
        width=stroke,
    )
    draw.rectangle([bx0, by0, bx1, by1], outline=(0, 0, 0), width=stroke)
    draw.polygon(
        [(bx0 - 10, by0), ((bx0 + bx1) // 2, int(h * 0.26)), (bx1 + 10, by0)],
        outline=(0, 0, 0),
        width=stroke,
    )
    tower_x = (bx0 + bx1) // 2
    draw.rectangle(
        [tower_x - int(w * 0.03), int(h * 0.22), tower_x + int(w * 0.03), by0],
        outline=(0, 0, 0),
        width=stroke,
    )
    draw.polygon(
        [
            (tower_x - int(w * 0.045), int(h * 0.22)),
            (tower_x, int(h * 0.12)),
            (tower_x + int(w * 0.045), int(h * 0.22)),
        ],
        outline=(0, 0, 0),
        width=stroke,
    )
    # intact cross
    cx, cy = tower_x, int(h * 0.09)
    line_ink([(cx, cy - int(h * 0.04)), (cx, cy + int(h * 0.05))], stroke + 2)
    line_ink([(cx - int(w * 0.025), cy), (cx + int(w * 0.025), cy)], stroke + 2)
    # door + windows
    draw.rounded_rectangle(
        [tower_x - int(w * 0.03), int(h * 0.54), tower_x + int(w * 0.03), by1],
        radius=18,
        outline=(0, 0, 0),
        width=stroke,
    )
    for wx in (int(w * 0.24), int(w * 0.38)):
        draw.rounded_rectangle(
            [wx, int(h * 0.48), wx + int(w * 0.04), int(h * 0.62)],
            radius=12,
            outline=(0, 0, 0),
            width=max(4, stroke - 2),
        )
    # tree (massed canopy, not individual leaves)
    tx, ty = int(w * 0.78), int(h * 0.72)
    draw.rectangle(
        [tx - int(w * 0.02), int(h * 0.48), tx + int(w * 0.02), ty],
        outline=(0, 0, 0),
        width=stroke,
    )
    draw.ellipse(
        [tx - int(w * 0.12), int(h * 0.22), tx + int(w * 0.12), int(h * 0.52)],
        outline=(0, 0, 0),
        width=stroke,
    )
    # welcome table (empty — no basket/apple/bible)
    draw.rectangle(
        [int(w * 0.58), int(h * 0.62), int(w * 0.78), int(h * 0.68)],
        outline=(0, 0, 0),
        width=stroke,
    )
    draw.rectangle(
        [int(w * 0.60), int(h * 0.68), int(w * 0.63), int(h * 0.78)],
        outline=(0, 0, 0),
        width=max(4, stroke - 2),
    )
    draw.rectangle(
        [int(w * 0.73), int(h * 0.68), int(w * 0.76), int(h * 0.78)],
        outline=(0, 0, 0),
        width=max(4, stroke - 2),
    )
    # string lights from church to tree
    y_wire = int(h * 0.24)
    line_ink([(bx1, int(h * 0.30)), (tx - int(w * 0.08), y_wire)], max(4, stroke - 2))
    for i in range(6):
        t = (i + 0.5) / 6
        bx = int(bx1 * (1 - t) + (tx - w * 0.08) * t)
        by = int(h * 0.30 * (1 - t) + y_wire * t) + int(18 * (1 - abs(2 * t - 1)))
        draw.ellipse([bx - 7, by, bx + 7, by + 16], outline=(0, 0, 0), width=max(4, stroke - 3))
    # clouds
    draw.ellipse([int(w * 0.55), int(h * 0.06), int(w * 0.72), int(h * 0.16)], outline=(0, 0, 0), width=max(4, stroke - 2))
    draw.ellipse([int(w * 0.08), int(h * 0.08), int(w * 0.22), int(h * 0.16)], outline=(0, 0, 0), width=max(4, stroke - 2))

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG")
    return {
        "asset_id": "proc_search_background",
        "role": "search_background",
        "status": "accepted",
        "request_id": "procedural-search-background",
        "model": "procedural-lineart",
        "prompt": (
            "Black-and-white church fall festival grounds for a search-and-find "
            "background: church with intact cross, path, tree canopy, empty welcome "
            "table, string lights, clouds. Do not include lantern, pumpkin, apple, "
            "leaf, acorn, scarf, basket, or Bible. No letters."
        ),
        "file": str(path),
        "sha256": _sha256(path),
        "cost_usd": 0.0,
        "attempts": 1,
        "paid_call": False,
        "dpi": DPI,
        "width": width,
        "height": height,
        "excluded_targets": sorted(TARGET_DRAWERS),
    }


def write_provenance(record: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
