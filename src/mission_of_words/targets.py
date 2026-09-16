"""Unique unpaid procedural search-target silhouettes. No letters in artwork."""

from __future__ import annotations

import math

from PIL import ImageDraw

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
STROKE = 14

Draw = ImageDraw.ImageDraw
Box = tuple[int, int, int, int]


def _m(box: Box) -> tuple[int, int, int, int, int, int]:
    x0, y0, x1, y1 = box
    return x0, y0, x1, y1, x1 - x0, y1 - y0


def _stroke(box: Box) -> int:
    _x0, _y0, _x1, _y1, w, h = _m(box)
    return max(6, min(STROKE, round(min(w, h) / 16)))


def extra_apple(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 20, y0 + h * 0.18, x1 - 20, y1 - 12], fill=WHITE, outline=BLACK, width=s)
    draw.line([(x0 + w * 0.5, y0 + h * 0.22), (x0 + w * 0.58, y0 + h * 0.06)], fill=BLACK, width=s)
    draw.ellipse(
        [x0 + w * 0.60, y0 + h * 0.08, x0 + w * 0.84, y0 + h * 0.28],
        outline=BLACK,
        width=max(4, s // 2),
    )


def shared_loaf(draw: Draw, box: Box) -> None:
    loaf(draw, box)
    x0, y0, x1, y1, w, h = _m(box)
    draw.line(
        [(x0 + w * 0.28, y0 + h * 0.42), (x0 + w * 0.28, y1 - 18)],
        fill=BLACK,
        width=max(6, _stroke(box) // 2),
    )


def small_lantern(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    body = [x0 + w * 0.24, y0 + h * 0.32, x1 - w * 0.24, y1 - h * 0.14]
    draw.rounded_rectangle(body, radius=16, fill=WHITE, outline=BLACK, width=s)
    draw.arc([x0 + w * 0.32, y0 + 8, x1 - w * 0.32, y0 + h * 0.36], start=0, end=180, fill=BLACK, width=s)
    cx = (x0 + x1) / 2
    draw.line([(cx, body[1] + 8), (cx, body[3] - 8)], fill=BLACK, width=max(4, s // 2))


def season_leaf(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.16, y0 + 20, x1 - w * 0.16, y1 - 40], fill=WHITE, outline=BLACK, width=s)
    cx = (x0 + x1) / 2
    draw.line([(cx, y1 - 12), (cx, y0 + h * 0.55)], fill=BLACK, width=s)
    draw.line([(cx, y0 + h * 0.55), (x0 + w * 0.22, y0 + h * 0.70)], fill=BLACK, width=max(4, s // 2))
    draw.line([(cx, y0 + h * 0.55), (x1 - w * 0.22, y0 + h * 0.70)], fill=BLACK, width=max(4, s // 2))


def oak_leaf(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.18, y0 + 16, x1 - w * 0.18, y1 - 24], fill=WHITE, outline=BLACK, width=s)
    for yy in (0.32, 0.48, 0.64):
        draw.arc(
            [x0 + w * 0.10, y0 + h * yy, x0 + w * 0.40, y0 + h * (yy + 0.18)],
            start=90,
            end=270,
            fill=BLACK,
            width=max(4, s // 2),
        )
        draw.arc(
            [x1 - w * 0.40, y0 + h * yy, x1 - w * 0.10, y0 + h * (yy + 0.18)],
            start=270,
            end=90,
            fill=BLACK,
            width=max(4, s // 2),
        )
    draw.line([(x0 + w * 0.5, y1 - 8), (x0 + w * 0.5, y0 + h * 0.28)], fill=BLACK, width=s)


def sun_disk(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(w, h) * 0.28
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=BLACK, width=s)
    for i in range(8):
        ang = math.radians(i * 45)
        draw.line(
            [
                (cx + r * 1.2 * math.cos(ang), cy + r * 1.2 * math.sin(ang)),
                (cx + r * 1.55 * math.cos(ang), cy + r * 1.55 * math.sin(ang)),
            ],
            fill=BLACK,
            width=max(6, s // 2),
        )


def crescent_moon(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.18, y0 + h * 0.16, x1 - w * 0.18, y1 - h * 0.16], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse(
        [x0 + w * 0.38, y0 + h * 0.12, x1 - w * 0.08, y1 - h * 0.20],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )


def star(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(w, h) * 0.42
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=WHITE, outline=BLACK, width=_stroke(box))


def cloud(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.12, y0 + h * 0.38, x0 + w * 0.52, y1 - h * 0.18], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.32, y0 + h * 0.22, x0 + w * 0.72, y1 - h * 0.22], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.50, y0 + h * 0.40, x1 - w * 0.10, y1 - h * 0.16], fill=WHITE, outline=BLACK, width=s)


def sundial(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 16, y0 + h * 0.28, x1 - 16, y1 - 12], fill=WHITE, outline=BLACK, width=s)
    cx, cy = (x0 + x1) / 2, y0 + h * 0.62
    draw.polygon(
        [(cx, cy), (cx + w * 0.18, y0 + h * 0.34), (cx + w * 0.08, cy)],
        fill=WHITE,
        outline=BLACK,
        width=max(4, s // 2),
    )
    draw.rectangle([x0 + w * 0.42, y1 - 28, x1 - w * 0.42, y1 - 8], outline=BLACK, width=max(4, s // 2))


def hourglass(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + w * 0.22, y0 + 16),
            (x1 - w * 0.22, y0 + 16),
            (x0 + w * 0.5, y0 + h * 0.5),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.polygon(
        [
            (x0 + w * 0.5, y0 + h * 0.5),
            (x1 - w * 0.22, y1 - 16),
            (x0 + w * 0.22, y1 - 16),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )


def sparrow(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.18, y0 + h * 0.38, x1 - w * 0.22, y1 - h * 0.22], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x1 - w * 0.40, y0 + h * 0.22, x1 - w * 0.08, y0 + h * 0.52], fill=WHITE, outline=BLACK, width=s)
    draw.polygon(
        [
            (x0 + w * 0.20, y0 + h * 0.50),
            (x0 + 8, y0 + h * 0.32),
            (x0 + w * 0.28, y0 + h * 0.42),
        ],
        fill=WHITE,
        outline=BLACK,
        width=max(4, s // 2),
    )
    draw.polygon(
        [
            (x1 - w * 0.12, y0 + h * 0.36),
            (x1 - 4, y0 + h * 0.40),
            (x1 - w * 0.12, y0 + h * 0.44),
        ],
        fill=WHITE,
        outline=BLACK,
        width=max(4, s // 2),
    )


def wheat_sheaf(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    cx = (x0 + x1) / 2
    draw.line([(cx, y1 - 8), (cx, y0 + h * 0.28)], fill=BLACK, width=s)
    for dx, top in ((-0.16, 0.18), (0.16, 0.16), (-0.08, 0.12), (0.08, 0.12)):
        draw.line([(cx, y0 + h * 0.55), (cx + w * dx, y0 + h * top)], fill=BLACK, width=max(4, s // 2))
        draw.ellipse(
            [cx + w * dx - 10, y0 + h * top - 8, cx + w * dx + 10, y0 + h * top + 18],
            outline=BLACK,
            width=max(4, s // 2),
        )
    draw.arc([cx - w * 0.18, y0 + h * 0.52, cx + w * 0.18, y0 + h * 0.78], start=200, end=340, fill=BLACK, width=s)


def corn_cob(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + w * 0.32, y0 + 20, x1 - w * 0.32, y1 - 16], radius=28, fill=WHITE, outline=BLACK, width=s)
    for row in range(4):
        for col in range(2):
            cx = x0 + w * (0.42 + col * 0.16)
            cy = y0 + h * (0.28 + row * 0.16)
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=BLACK, width=max(3, s // 3))
    draw.polygon(
        [(x0 + w * 0.38, y0 + 22), (x0 + w * 0.5, y0 + 6), (x1 - w * 0.38, y0 + 22)],
        outline=BLACK,
        width=max(4, s // 2),
    )


def loaf(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 18, y0 + h * 0.32, x1 - 18, y1 - 16], fill=WHITE, outline=BLACK, width=s)
    draw.arc([x0 + w * 0.22, y0 + h * 0.22, x0 + w * 0.48, y0 + h * 0.55], start=200, end=340, fill=BLACK, width=max(4, s // 2))
    draw.arc([x0 + w * 0.50, y0 + h * 0.22, x0 + w * 0.76, y0 + h * 0.55], start=200, end=340, fill=BLACK, width=max(4, s // 2))


def pitcher(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + w * 0.30, y0 + h * 0.22),
            (x1 - w * 0.30, y0 + h * 0.22),
            (x1 - w * 0.22, y1 - 16),
            (x0 + w * 0.22, y1 - 16),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.arc([x1 - w * 0.38, y0 + h * 0.28, x1 - 4, y0 + h * 0.70], start=270, end=90, fill=BLACK, width=s)
    draw.ellipse([x0 + w * 0.32, y0 + 12, x1 - w * 0.32, y0 + h * 0.28], outline=BLACK, width=s)


def pie(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 16, y0 + h * 0.22, x1 - 16, y1 - 12], fill=WHITE, outline=BLACK, width=s)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + h * 0.06
    draw.line([(cx, cy), (cx, y0 + h * 0.28)], fill=BLACK, width=max(4, s // 2))
    draw.line([(cx, cy), (x1 - 28, cy + 8)], fill=BLACK, width=max(4, s // 2))
    draw.line([(cx, cy), (x0 + 28, cy + 8)], fill=BLACK, width=max(4, s // 2))


def hymn_book(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + 20, y0 + 24, x1 - 20, y1 - 16], radius=12, fill=WHITE, outline=BLACK, width=s)
    draw.line([(x0 + w * 0.28, y0 + 24), (x0 + w * 0.28, y1 - 16)], fill=BLACK, width=max(4, s // 2))
    draw.line([(x0 + w * 0.42, y0 + h * 0.42), (x1 - w * 0.28, y0 + h * 0.42)], fill=BLACK, width=max(4, s // 2))
    draw.line([(x0 + w * 0.42, y0 + h * 0.54), (x1 - w * 0.32, y0 + h * 0.54)], fill=BLACK, width=max(4, s // 2))


def heart(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    cx = (x0 + x1) / 2
    draw.ellipse([x0 + w * 0.14, y0 + h * 0.22, cx + 4, y0 + h * 0.62], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([cx - 4, y0 + h * 0.22, x1 - w * 0.14, y0 + h * 0.62], fill=WHITE, outline=BLACK, width=s)
    draw.polygon(
        [(x0 + w * 0.16, y0 + h * 0.48), (cx, y1 - 16), (x1 - w * 0.16, y0 + h * 0.48)],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )


def thank_you_card(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + 18, y0 + 20, x1 - 18, y1 - 18], radius=10, fill=WHITE, outline=BLACK, width=s)
    heart(draw, (int(x0 + w * 0.30), int(y0 + h * 0.32), int(x1 - w * 0.30), int(y1 - h * 0.28)))


def hiking_boot(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + w * 0.12, y0 + h * 0.48),
            (x1 - w * 0.10, y0 + h * 0.52),
            (x1 - w * 0.08, y1 - 20),
            (x0 + w * 0.10, y1 - 18),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.rounded_rectangle([x0 + w * 0.12, y0 + h * 0.18, x0 + w * 0.48, y0 + h * 0.55], radius=16, outline=BLACK, width=s)
    draw.line([(x0 + w * 0.18, y1 - 28), (x1 - w * 0.16, y1 - 30)], fill=BLACK, width=max(4, s // 2))


def walking_stick(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.line([(x0 + w * 0.42, y1 - 12), (x0 + w * 0.58, y0 + 24)], fill=BLACK, width=s + 2)
    draw.arc([x0 + w * 0.42, y0 + 8, x1 - w * 0.18, y0 + h * 0.32], start=200, end=20, fill=BLACK, width=s)


def trail_map(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + 22, y0 + 28),
            (x1 - 18, y0 + 22),
            (x1 - 24, y1 - 18),
            (x0 + 18, y1 - 24),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.line([(x0 + w * 0.28, y0 + h * 0.40), (x0 + w * 0.62, y0 + h * 0.52), (x0 + w * 0.48, y0 + h * 0.72)], fill=BLACK, width=max(4, s // 2))


def compass(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 18, y0 + 18, x1 - 18, y1 - 18], fill=WHITE, outline=BLACK, width=s)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw.polygon([(cx, y0 + 36), (cx + 10, cy), (cx, y1 - 36), (cx - 10, cy)], fill=WHITE, outline=BLACK, width=max(4, s // 2))


def owl(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.22, y0 + h * 0.22, x1 - w * 0.22, y1 - 16], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.28, y0 + h * 0.28, x0 + w * 0.48, y0 + h * 0.50], outline=BLACK, width=max(4, s // 2))
    draw.ellipse([x1 - w * 0.48, y0 + h * 0.28, x1 - w * 0.28, y0 + h * 0.50], outline=BLACK, width=max(4, s // 2))
    draw.polygon(
        [(x0 + w * 0.46, y0 + h * 0.52), (x0 + w * 0.54, y0 + h * 0.52), (x0 + w * 0.50, y0 + h * 0.62)],
        outline=BLACK,
        width=max(4, s // 2),
    )


def blanket(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + 16, y0 + 20, x1 - 16, y1 - 16], radius=8, fill=WHITE, outline=BLACK, width=s)
    for i in range(3):
        yy = y0 + h * (0.35 + i * 0.18)
        draw.line([(x0 + 28, yy), (x1 - 28, yy)], fill=BLACK, width=max(4, s // 2))


def brave_badge(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 24, y0 + 16, x1 - 24, y1 - 48], fill=WHITE, outline=BLACK, width=s)
    draw.polygon(
        [(x0 + w * 0.32, y1 - 52), (x0 + w * 0.50, y1 - 16), (x1 - w * 0.32, y1 - 52)],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    star(draw, (int(x0 + w * 0.32), int(y0 + h * 0.18), int(x1 - w * 0.32), int(y0 + h * 0.62)))


def soup_pot(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + w * 0.18, y0 + h * 0.32, x1 - w * 0.18, y1 - 16], radius=18, fill=WHITE, outline=BLACK, width=s)
    draw.line([(x0 + 8, y0 + h * 0.42), (x0 + w * 0.18, y0 + h * 0.42)], fill=BLACK, width=s)
    draw.line([(x1 - 8, y0 + h * 0.42), (x1 - w * 0.18, y0 + h * 0.42)], fill=BLACK, width=s)
    draw.ellipse([x0 + w * 0.18, y0 + h * 0.22, x1 - w * 0.18, y0 + h * 0.42], outline=BLACK, width=s)


def empty_bowl(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + w * 0.16, y0 + h * 0.42),
            (x1 - w * 0.16, y0 + h * 0.42),
            (x1 - w * 0.28, y1 - 18),
            (x0 + w * 0.28, y1 - 18),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.ellipse([x0 + w * 0.16, y0 + h * 0.28, x1 - w * 0.16, y0 + h * 0.52], outline=BLACK, width=s)


def pair_of_gloves(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    for dx in (0.08, 0.46):
        draw.rounded_rectangle(
            [x0 + w * dx, y0 + h * 0.28, x0 + w * (dx + 0.38), y1 - 16],
            radius=22,
            fill=WHITE,
            outline=BLACK,
            width=s,
        )
        draw.ellipse(
            [x0 + w * (dx + 0.22), y0 + 12, x0 + w * (dx + 0.38), y0 + h * 0.36],
            outline=BLACK,
            width=max(4, s // 2),
        )


def jam_jar(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + w * 0.28, y0 + h * 0.28, x1 - w * 0.28, y1 - 16], radius=12, fill=WHITE, outline=BLACK, width=s)
    draw.rectangle([x0 + w * 0.24, y0 + 16, x1 - w * 0.24, y0 + h * 0.32], outline=BLACK, width=s)
    draw.line([(x0 + w * 0.34, y0 + h * 0.55), (x1 - w * 0.34, y0 + h * 0.55)], fill=BLACK, width=max(4, s // 2))


def note_card(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rectangle([x0 + 20, y0 + 18, x1 - 20, y1 - 18], fill=WHITE, outline=BLACK, width=s)
    draw.line([(x0 + 36, y0 + h * 0.40), (x1 - 36, y0 + h * 0.40)], fill=BLACK, width=max(4, s // 2))
    draw.line([(x0 + 36, y0 + h * 0.52), (x1 - 48, y0 + h * 0.52)], fill=BLACK, width=max(4, s // 2))
    draw.line([(x0 + 36, y0 + h * 0.64), (x1 - 40, y0 + h * 0.64)], fill=BLACK, width=max(4, s // 2))


def wagon(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rectangle([x0 + w * 0.12, y0 + h * 0.38, x1 - w * 0.12, y0 + h * 0.70], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.16, y0 + h * 0.62, x0 + w * 0.40, y1 - 10], outline=BLACK, width=s)
    draw.ellipse([x1 - w * 0.40, y0 + h * 0.62, x1 - w * 0.16, y1 - 10], outline=BLACK, width=s)
    draw.line([(x1 - w * 0.12, y0 + h * 0.48), (x1 - 8, y0 + h * 0.32)], fill=BLACK, width=s)


def ticket(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + 12, y0 + h * 0.32, x1 - 12, y1 - h * 0.32], radius=8, fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + 6, y0 + h * 0.42, x0 + 28, y0 + h * 0.58], fill=WHITE, outline=BLACK, width=max(4, s // 2))
    draw.ellipse([x1 - 28, y0 + h * 0.42, x1 - 6, y0 + h * 0.58], fill=WHITE, outline=BLACK, width=max(4, s // 2))
    draw.line([(x0 + w * 0.30, y0 + h * 0.40), (x0 + w * 0.30, y1 - h * 0.40)], fill=BLACK, width=max(4, s // 2))


def cider_cup(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + w * 0.28, y0 + h * 0.22),
            (x1 - w * 0.28, y0 + h * 0.22),
            (x1 - w * 0.34, y1 - 16),
            (x0 + w * 0.34, y1 - 16),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.arc([x1 - w * 0.40, y0 + h * 0.30, x1 - 8, y0 + h * 0.62], start=270, end=90, fill=BLACK, width=s)


def kind_note(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + 20, y0 + 28),
            (x1 - 20, y0 + 22),
            (x1 - 28, y1 - 20),
            (x0 + 18, y1 - 16),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    heart(draw, (int(x0 + w * 0.32), int(y0 + h * 0.34), int(x1 - w * 0.32), int(y1 - h * 0.28)))


def extra_chair(draw: Draw, box: Box) -> None:
    chair(draw, box)
    x0, y0, x1, y1, w, h = _m(box)
    draw.ellipse([x0 + w * 0.70, y0 + 12, x1 - 12, y0 + 40], outline=BLACK, width=max(4, _stroke(box) // 2))


def chair(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rectangle([x0 + w * 0.18, y0 + h * 0.48, x1 - w * 0.18, y0 + h * 0.62], fill=WHITE, outline=BLACK, width=s)
    draw.rectangle([x0 + w * 0.22, y0 + 16, x0 + w * 0.34, y0 + h * 0.50], outline=BLACK, width=s)
    draw.rectangle([x1 - w * 0.34, y0 + 16, x1 - w * 0.22, y0 + h * 0.50], outline=BLACK, width=s)
    draw.rectangle([x0 + w * 0.22, y0 + h * 0.60, x1 - w * 0.22, y1 - 16], outline=BLACK, width=s)


def smile_badge(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 20, y0 + 20, x1 - 20, y1 - 20], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.34, y0 + h * 0.36, x0 + w * 0.44, y0 + h * 0.48], outline=BLACK, width=max(4, s // 2))
    draw.ellipse([x1 - w * 0.44, y0 + h * 0.36, x1 - w * 0.34, y0 + h * 0.48], outline=BLACK, width=max(4, s // 2))
    draw.arc([x0 + w * 0.32, y0 + h * 0.46, x1 - w * 0.32, y1 - h * 0.28], start=200, end=340, fill=BLACK, width=s)


def bandage(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rounded_rectangle([x0 + 16, y0 + h * 0.38, x1 - 16, y1 - h * 0.38], radius=12, fill=WHITE, outline=BLACK, width=s)
    draw.rectangle([x0 + w * 0.38, y0 + h * 0.38, x1 - w * 0.38, y1 - h * 0.38], outline=BLACK, width=max(4, s // 2))


def shared_pretzel(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.arc([x0 + 24, y0 + 24, x1 - 24, y1 - 24], start=20, end=340, fill=BLACK, width=s + 4)
    draw.ellipse([x0 + w * 0.30, y0 + h * 0.30, x0 + w * 0.48, y0 + h * 0.48], outline=BLACK, width=s)
    draw.ellipse([x1 - w * 0.48, y0 + h * 0.30, x1 - w * 0.30, y0 + h * 0.48], outline=BLACK, width=s)


def game_ring(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 28, y0 + 28, x1 - 28, y1 - 28], outline=BLACK, width=s + 6)
    draw.ellipse([x0 + 56, y0 + 56, x1 - 56, y1 - 56], outline=BLACK, width=max(4, s // 2))


def pinecone(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.28, y0 + 16, x1 - w * 0.28, y1 - 12], fill=WHITE, outline=BLACK, width=s)
    for i in range(4):
        yy = y0 + h * (0.28 + i * 0.16)
        draw.arc([x0 + w * 0.30, yy, x1 - w * 0.30, yy + h * 0.18], start=200, end=340, fill=BLACK, width=max(4, s // 2))


def deer(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.16, y0 + h * 0.40, x1 - w * 0.28, y1 - h * 0.22], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x1 - w * 0.42, y0 + h * 0.18, x1 - w * 0.12, y0 + h * 0.48], fill=WHITE, outline=BLACK, width=s)
    draw.line([(x1 - w * 0.28, y0 + h * 0.20), (x1 - w * 0.36, y0 + 8)], fill=BLACK, width=s)
    draw.line([(x1 - w * 0.20, y0 + h * 0.20), (x1 - w * 0.12, y0 + 8)], fill=BLACK, width=s)
    for dx in (0.24, 0.38, 0.52, 0.64):
        draw.line([(x0 + w * dx, y1 - h * 0.24), (x0 + w * dx, y1 - 8)], fill=BLACK, width=max(4, s // 2))


def creek_fish(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 20, y0 + h * 0.32, x1 - w * 0.28, y1 - h * 0.32], fill=WHITE, outline=BLACK, width=s)
    draw.polygon(
        [(x1 - w * 0.32, y0 + h * 0.5), (x1 - 12, y0 + h * 0.28), (x1 - 12, y1 - h * 0.28)],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.ellipse([x0 + w * 0.32, y0 + h * 0.44, x0 + w * 0.40, y0 + h * 0.56], outline=BLACK, width=max(4, s // 2))


def mushroom(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.pieslice([x0 + 16, y0 + 16, x1 - 16, y0 + h * 0.70], start=180, end=360, fill=WHITE, outline=BLACK, width=s)
    draw.rectangle([x0 + w * 0.40, y0 + h * 0.48, x1 - w * 0.40, y1 - 16], outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.30, y0 + h * 0.28, x0 + w * 0.42, y0 + h * 0.40], outline=BLACK, width=max(3, s // 3))


def bird_nest(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 18, y0 + h * 0.38, x1 - 18, y1 - 16], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + 40, y0 + h * 0.46, x1 - 40, y1 - 36], outline=BLACK, width=max(4, s // 2))
    draw.ellipse([x0 + w * 0.38, y0 + h * 0.22, x0 + w * 0.52, y0 + h * 0.42], outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.50, y0 + h * 0.24, x0 + w * 0.64, y0 + h * 0.44], outline=BLACK, width=s)


def pebble(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 24, y0 + h * 0.32, x1 - 20, y1 - 20], fill=WHITE, outline=BLACK, width=s)
    draw.arc([x0 + w * 0.32, y0 + h * 0.40, x0 + w * 0.62, y0 + h * 0.62], start=200, end=20, fill=BLACK, width=max(4, s // 2))


def ladybug(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.18, y0 + h * 0.30, x1 - w * 0.18, y1 - 16], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + w * 0.34, y0 + 16, x1 - w * 0.34, y0 + h * 0.40], outline=BLACK, width=s)
    draw.line([(x0 + w * 0.5, y0 + h * 0.38), (x0 + w * 0.5, y1 - 20)], fill=BLACK, width=max(4, s // 2))
    for cx, cy in ((0.34, 0.52), (0.66, 0.52), (0.38, 0.70), (0.62, 0.70)):
        draw.ellipse([x0 + w * cx - 6, y0 + h * cy - 6, x0 + w * cx + 6, y0 + h * cy + 6], outline=BLACK, width=max(3, s // 3))


def plate(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + 12, y0 + 18, x1 - 12, y1 - 18], fill=WHITE, outline=BLACK, width=s)
    draw.ellipse([x0 + 48, y0 + 54, x1 - 48, y1 - 54], outline=BLACK, width=max(4, s // 2))


def cup(draw: Draw, box: Box) -> None:
    cider_cup(draw, box)


def napkin(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [(x0 + 24, y0 + 28), (x1 - 20, y0 + 22), (x1 - 28, y1 - 20), (x0 + 18, y1 - 24)],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.line([(x0 + w * 0.28, y0 + h * 0.28), (x1 - w * 0.34, y1 - h * 0.28)], fill=BLACK, width=max(4, s // 2))


def bread_basket(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [
            (x0 + w * 0.12, y0 + h * 0.52),
            (x1 - w * 0.12, y0 + h * 0.52),
            (x1 - w * 0.22, y1 - 16),
            (x0 + w * 0.22, y1 - 16),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.arc([x0 + w * 0.16, y0 + h * 0.12, x1 - w * 0.16, y0 + h * 0.70], start=0, end=180, fill=BLACK, width=s)
    draw.ellipse([x0 + w * 0.32, y0 + h * 0.28, x1 - w * 0.32, y0 + h * 0.52], outline=BLACK, width=max(4, s // 2))


def candle(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.rectangle([x0 + w * 0.38, y0 + h * 0.32, x1 - w * 0.38, y1 - 16], fill=WHITE, outline=BLACK, width=s)
    draw.polygon(
        [
            (x0 + w * 0.50, y0 + 8),
            (x0 + w * 0.58, y0 + h * 0.28),
            (x0 + w * 0.42, y0 + h * 0.28),
        ],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )


def place_card(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.polygon(
        [(x0 + 18, y1 - 28), (x1 - 18, y1 - 28), (x0 + w * 0.50, y0 + 24)],
        fill=WHITE,
        outline=BLACK,
        width=s,
    )
    draw.line([(x0 + 18, y1 - 28), (x1 - 18, y1 - 28)], fill=BLACK, width=s)


def serving_spoon(draw: Draw, box: Box) -> None:
    x0, y0, x1, y1, w, h = _m(box)
    s = _stroke(box)
    draw.ellipse([x0 + w * 0.22, y0 + 12, x1 - w * 0.22, y0 + h * 0.48], fill=WHITE, outline=BLACK, width=s)
    draw.rectangle([x0 + w * 0.44, y0 + h * 0.44, x1 - w * 0.44, y1 - 12], outline=BLACK, width=s)


SEARCH_TARGET_DRAWERS = {
    "sun_disk": sun_disk,
    "crescent_moon": crescent_moon,
    "star": star,
    "cloud": cloud,
    "sundial": sundial,
    "hourglass": hourglass,
    "sparrow": sparrow,
    "season_leaf": season_leaf,
    "wheat_sheaf": wheat_sheaf,
    "corn_cob": corn_cob,
    "loaf": loaf,
    "pitcher": pitcher,
    "pie": pie,
    "hymn_book": hymn_book,
    "heart": heart,
    "thank_you_card": thank_you_card,
    "hiking_boot": hiking_boot,
    "walking_stick": walking_stick,
    "small_lantern": small_lantern,
    "trail_map": trail_map,
    "compass": compass,
    "owl": owl,
    "blanket": blanket,
    "brave_badge": brave_badge,
    "extra_apple": extra_apple,
    "shared_loaf": shared_loaf,
    "soup_pot": soup_pot,
    "empty_bowl": empty_bowl,
    "pair_of_gloves": pair_of_gloves,
    "jam_jar": jam_jar,
    "note_card": note_card,
    "wagon": wagon,
    "ticket": ticket,
    "cider_cup": cider_cup,
    "kind_note": kind_note,
    "extra_chair": extra_chair,
    "smile_badge": smile_badge,
    "bandage": bandage,
    "shared_pretzel": shared_pretzel,
    "game_ring": game_ring,
    "oak_leaf": oak_leaf,
    "pinecone": pinecone,
    "deer": deer,
    "creek_fish": creek_fish,
    "mushroom": mushroom,
    "bird_nest": bird_nest,
    "pebble": pebble,
    "ladybug": ladybug,
    "plate": plate,
    "cup": cup,
    "napkin": napkin,
    "chair": chair,
    "bread_basket": bread_basket,
    "candle": candle,
    "place_card": place_card,
    "serving_spoon": serving_spoon,
}


def display_name(name: str) -> str:
    if name == "Bible":
        return "Bible"
    return name.replace("_", " ")
