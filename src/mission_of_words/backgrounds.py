"""Unique unpaid search-and-find backgrounds. Each mission gets its own scene.

Backgrounds must not include that mission's eight search targets.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

BLACK = (0, 0, 0)


def _stroke(width: int, height: int) -> int:
    return max(8, round(min(width, height) / 180))


def _line(draw: ImageDraw.ImageDraw, xy, width: int) -> None:
    draw.line(xy, fill=BLACK, width=width)


def festival_grounds(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    ground_y = int(h * 0.72)
    draw.polygon([(0, ground_y), (w, int(h * 0.70)), (w, h), (0, h)], outline=BLACK, width=stroke)
    bx0, by0 = int(w * 0.18), int(h * 0.38)
    bx1, by1 = int(w * 0.48), ground_y
    draw.polygon(
        [(int(w * 0.40), h), (int(w * 0.60), h), (int(w * 0.52), by1), (int(w * 0.44), by1)],
        outline=BLACK,
        width=stroke,
    )
    draw.rectangle([bx0, by0, bx1, by1], outline=BLACK, width=stroke)
    draw.polygon([(bx0 - 10, by0), ((bx0 + bx1) // 2, int(h * 0.26)), (bx1 + 10, by0)], outline=BLACK, width=stroke)
    tower_x = (bx0 + bx1) // 2
    draw.rectangle([tower_x - int(w * 0.03), int(h * 0.22), tower_x + int(w * 0.03), by0], outline=BLACK, width=stroke)
    draw.polygon(
        [(tower_x - int(w * 0.045), int(h * 0.22)), (tower_x, int(h * 0.12)), (tower_x + int(w * 0.045), int(h * 0.22))],
        outline=BLACK,
        width=stroke,
    )
    cx, cy = tower_x, int(h * 0.09)
    _line(draw, [(cx, cy - int(h * 0.04)), (cx, cy + int(h * 0.05))], stroke + 2)
    _line(draw, [(cx - int(w * 0.025), cy), (cx + int(w * 0.025), cy)], stroke + 2)
    draw.rounded_rectangle([tower_x - int(w * 0.03), int(h * 0.54), tower_x + int(w * 0.03), by1], radius=18, outline=BLACK, width=stroke)
    tx, ty = int(w * 0.78), int(h * 0.72)
    draw.rectangle([tx - int(w * 0.02), int(h * 0.48), tx + int(w * 0.02), ty], outline=BLACK, width=stroke)
    draw.ellipse([tx - int(w * 0.12), int(h * 0.22), tx + int(w * 0.12), int(h * 0.52)], outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.58), int(h * 0.62), int(w * 0.78), int(h * 0.68)], outline=BLACK, width=stroke)
    y_wire = int(h * 0.24)
    _line(draw, [(bx1, int(h * 0.30)), (tx - int(w * 0.08), y_wire)], max(4, stroke - 2))
    draw.ellipse([int(w * 0.55), int(h * 0.06), int(w * 0.72), int(h * 0.16)], outline=BLACK, width=max(4, stroke - 2))
    return "Church festival grounds without the eight independently placed gifts."


def dusk_orchard(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.polygon([(0, int(h * 0.62)), (w, int(h * 0.58)), (w, h), (0, h)], outline=BLACK, width=stroke)
    for tx, canopy in ((0.18, 0.16), (0.48, 0.20), (0.78, 0.15)):
        x = int(w * tx)
        draw.rectangle([x - int(w * 0.015), int(h * 0.42), x + int(w * 0.015), int(h * 0.68)], outline=BLACK, width=stroke)
        draw.ellipse([x - int(w * canopy), int(h * 0.18), x + int(w * canopy), int(h * 0.48)], outline=BLACK, width=stroke)
    _line(draw, [(int(w * 0.10), int(h * 0.78)), (int(w * 0.90), int(h * 0.70))], stroke)
    draw.arc([int(w * 0.62), int(h * 0.08), int(w * 0.92), int(h * 0.32)], start=20, end=200, fill=BLACK, width=stroke)
    return "Dusk orchard hillside without sun, moon, star, cloud, sundial, hourglass, sparrow, or season leaf."


def barn_yard(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.polygon([(0, int(h * 0.68)), (w, int(h * 0.64)), (w, h), (0, h)], outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.18), int(h * 0.32), int(w * 0.62), int(h * 0.68)], outline=BLACK, width=stroke)
    draw.polygon(
        [(int(w * 0.12), int(h * 0.32)), (int(w * 0.40), int(h * 0.12)), (int(w * 0.68), int(h * 0.32))],
        outline=BLACK,
        width=stroke,
    )
    draw.rounded_rectangle([int(w * 0.34), int(h * 0.46), int(w * 0.46), int(h * 0.68)], radius=16, outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.70), int(h * 0.52), int(w * 0.92), int(h * 0.66)], outline=BLACK, width=stroke)
    return "Barn yard without wheat, corn, loaf, pitcher, pie, hymn book, heart, or thank-you card."


def woods_path(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.polygon([(0, int(h * 0.70)), (w, int(h * 0.66)), (w, h), (0, h)], outline=BLACK, width=stroke)
    for tx in (0.14, 0.38, 0.62, 0.86):
        x = int(w * tx)
        draw.rectangle([x - 8, int(h * 0.36), x + 8, int(h * 0.72)], outline=BLACK, width=stroke)
        draw.ellipse([x - int(w * 0.10), int(h * 0.12), x + int(w * 0.10), int(h * 0.42)], outline=BLACK, width=stroke)
    draw.polygon(
        [(int(w * 0.28), h), (int(w * 0.48), h), (int(w * 0.42), int(h * 0.70)), (int(w * 0.34), int(h * 0.70))],
        outline=BLACK,
        width=stroke,
    )
    draw.rectangle([int(w * 0.72), int(h * 0.48), int(w * 0.96), int(h * 0.72)], outline=BLACK, width=stroke)
    return "Autumn woods path without boot, stick, lantern, map, compass, owl, blanket, or badge."


def neighbor_porch(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.polygon([(0, int(h * 0.74)), (w, int(h * 0.70)), (w, h), (0, h)], outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.28), int(h * 0.22), int(w * 0.88), int(h * 0.74)], outline=BLACK, width=stroke)
    draw.polygon(
        [(int(w * 0.20), int(h * 0.22)), (int(w * 0.58), int(h * 0.06)), (int(w * 0.96), int(h * 0.22))],
        outline=BLACK,
        width=stroke,
    )
    draw.rounded_rectangle([int(w * 0.48), int(h * 0.42), int(w * 0.64), int(h * 0.74)], radius=18, outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.28), int(h * 0.62), int(w * 0.88), int(h * 0.68)], outline=BLACK, width=stroke)
    return "Neighbor porch without apple, loaf, pot, bowl, gloves, jam, note, or wagon."


def festival_booths(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.polygon([(0, int(h * 0.70)), (w, int(h * 0.68)), (w, h), (0, h)], outline=BLACK, width=stroke)
    for x0, x1 in ((0.08, 0.38), (0.42, 0.72), (0.76, 0.98)):
        draw.rectangle([int(w * x0), int(h * 0.42), int(w * x1), int(h * 0.70)], outline=BLACK, width=stroke)
        draw.polygon(
            [
                (int(w * (x0 - 0.02)), int(h * 0.42)),
                (int(w * ((x0 + x1) / 2)), int(h * 0.28)),
                (int(w * (x1 + 0.02)), int(h * 0.42)),
            ],
            outline=BLACK,
            width=stroke,
        )
    return "Festival booths without ticket, cider, note, chair, badge, bandage, pretzel, or ring."


def hillside_creek(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.polygon([(0, int(h * 0.78)), (w, int(h * 0.52)), (w, h), (0, h)], outline=BLACK, width=stroke)
    p = [(int(w * 0.05), int(h * 0.82)), (int(w * 0.35), int(h * 0.70)), (int(w * 0.70), int(h * 0.86)), (int(w * 0.95), int(h * 0.72))]
    _line(draw, p, stroke)
    _line(draw, [(x, y + int(h * 0.08)) for x, y in p], stroke)
    for tx in (0.22, 0.58, 0.84):
        x = int(w * tx)
        draw.rectangle([x - 7, int(h * 0.30), x + 7, int(h * 0.62)], outline=BLACK, width=stroke)
        draw.ellipse([x - int(w * 0.11), int(h * 0.10), x + int(w * 0.11), int(h * 0.38)], outline=BLACK, width=stroke)
    return "Hillside creek without oak leaf, pinecone, deer, fish, mushroom, nest, pebble, or ladybug."


def dining_room(draw: ImageDraw.ImageDraw, w: int, h: int) -> str:
    stroke = _stroke(w, h)
    draw.rectangle([0, int(h * 0.62), w, h], outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.16), int(h * 0.48), int(w * 0.84), int(h * 0.58)], outline=BLACK, width=stroke)
    draw.rectangle([int(w * 0.22), int(h * 0.58), int(w * 0.28), int(h * 0.78)], outline=BLACK, width=max(4, stroke - 2))
    draw.rectangle([int(w * 0.72), int(h * 0.58), int(w * 0.78), int(h * 0.78)], outline=BLACK, width=max(4, stroke - 2))
    draw.rectangle([int(w * 0.08), int(h * 0.10), int(w * 0.42), int(h * 0.38)], outline=BLACK, width=stroke)
    _line(draw, [(int(w * 0.25), int(h * 0.10)), (int(w * 0.25), int(h * 0.38))], max(4, stroke - 2))
    _line(draw, [(int(w * 0.08), int(h * 0.24)), (int(w * 0.42), int(h * 0.24))], max(4, stroke - 2))
    return "Dining room without plate, cup, napkin, chair, bread basket, candle, place card, or spoon."


THEMES = {
    "mission_01": festival_grounds,
    "mission_02": dusk_orchard,
    "mission_03": barn_yard,
    "mission_04": woods_path,
    "mission_05": neighbor_porch,
    "mission_06": festival_booths,
    "mission_07": hillside_creek,
    "mission_08": dining_room,
    "festival": festival_grounds,
}


def render_theme(image: Image.Image, theme: str) -> str:
    draw = ImageDraw.Draw(image)
    painter = THEMES.get(theme, festival_grounds)
    return painter(draw, image.width, image.height)
