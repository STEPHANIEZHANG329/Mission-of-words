"""Commercial-style black line art. Closed, colorable shapes. No letters."""

from __future__ import annotations

import math

from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas


def ink(c: canvas.Canvas, width: float = 1.8) -> None:
    c.setFillColor(white)
    c.setStrokeColor(black)
    c.setLineWidth(width)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setDash()


def _path(c: canvas.Canvas, points: list[tuple[float, float]], width: float, fill: int = 1) -> None:
    ink(c, width)
    p = c.beginPath()
    p.moveTo(*points[0])
    for x, y in points[1:]:
        p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=fill, stroke=1)


def oval(c: canvas.Canvas, x0: float, y0: float, x1: float, y1: float, width: float, fill: int = 1) -> None:
    ink(c, width)
    c.ellipse(x0, y0, x1, y1, fill=fill, stroke=1)


def circle(c: canvas.Canvas, cx: float, cy: float, r: float, width: float, fill: int = 1) -> None:
    ink(c, width)
    c.circle(cx, cy, r, fill=fill, stroke=1)


def rect(c: canvas.Canvas, x: float, y: float, w: float, h: float, width: float, fill: int = 1) -> None:
    ink(c, width)
    c.roundRect(x, y, w, h, min(6, abs(w), abs(h)) * 0.08, fill=fill, stroke=1)


def draw_cross(c: canvas.Canvas, cx: float, cy: float, size: float, width: float = 2.0) -> None:
    """Intact Latin cross. Vertical and horizontal bars share a solid center."""
    ink(c, width)
    arm = size * 0.32
    c.setFillColor(black)
    c.rect(cx - width * 0.55, cy - size * 0.08, width * 1.1, size, fill=1, stroke=0)
    c.rect(cx - arm, cy + size * 0.52, arm * 2, width * 1.1, fill=1, stroke=0)
    c.setFillColor(white)


def draw_lantern(c: canvas.Canvas, x: float, y: float, h: float) -> None:
    w = h * 0.62
    glass_b = y + h * 0.16
    glass_t = y + h * 0.72
    _path(
        c,
        [
            (x + w * 0.18, y),
            (x + w * 0.82, y),
            (x + w * 0.88, glass_b),
            (x + w * 0.12, glass_b),
        ],
        1.8,
    )
    rect(c, x + w * 0.12, glass_b, w * 0.76, glass_t - glass_b, 1.8)
    c.setStrokeColor(black)
    c.setLineWidth(1.3)
    c.line(x + w * 0.5, glass_b + 2, x + w * 0.5, glass_t - 2)
    c.line(x + w * 0.18, (glass_b + glass_t) / 2, x + w * 0.82, (glass_b + glass_t) / 2)
    # flame (closed teardrop)
    flame_h = h * 0.22
    fx, fy = x + w * 0.5, y + h * 0.28
    _path(
        c,
        [
            (fx, fy + flame_h),
            (fx + w * 0.12, fy + flame_h * 0.45),
            (fx + w * 0.08, fy),
            (fx - w * 0.08, fy),
            (fx - w * 0.12, fy + flame_h * 0.45),
        ],
        1.4,
    )
    _path(
        c,
        [
            (x + w * 0.08, glass_t),
            (x + w * 0.92, glass_t),
            (x + w * 0.78, y + h * 0.86),
            (x + w * 0.22, y + h * 0.86),
        ],
        1.8,
    )
    ink(c, 1.8)
    c.arc(x + w * 0.22, y + h * 0.78, x + w * 0.78, y + h * 1.08, 0, 180)


def draw_pumpkin(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 0.78
    oval(c, x, y, x + w, y + h, 1.8)
    ink(c, 1.3)
    c.arc(x + w * 0.22, y + h * 0.08, x + w * 0.48, y + h * 0.92, 250, 110)
    c.arc(x + w * 0.52, y + h * 0.08, x + w * 0.78, y + h * 0.92, 220, 110)
    rect(c, x + w * 0.44, y + h * 0.88, w * 0.12, h * 0.22, 1.6)


def draw_leaf(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 1.25
    oval(c, x + w * 0.12, y + h * 0.18, x + w * 0.88, y + h * 0.92, 1.6)
    ink(c, 1.3)
    c.line(x + w * 0.5, y, x + w * 0.5, y + h * 0.7)
    c.line(x + w * 0.5, y + h * 0.48, x + w * 0.22, y + h * 0.62)
    c.line(x + w * 0.5, y + h * 0.48, x + w * 0.78, y + h * 0.62)


def draw_apple(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    circle(c, x + w * 0.5, y + w * 0.42, w * 0.42, 1.7)
    ink(c, 1.5)
    c.line(x + w * 0.5, y + w * 0.82, x + w * 0.58, y + w * 1.02)
    # dimple, not a second fruit
    c.arc(x + w * 0.32, y + w * 0.68, x + w * 0.68, y + w * 0.92, 200, 140)


def draw_acorn(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 1.25
    oval(c, x + w * 0.12, y, x + w * 0.88, y + h * 0.7, 1.6)
    _path(
        c,
        [
            (x, y + h * 0.52),
            (x + w, y + h * 0.52),
            (x + w * 0.86, y + h * 0.78),
            (x + w * 0.14, y + h * 0.78),
        ],
        1.6,
    )
    ink(c, 1.4)
    c.line(x + w * 0.5, y + h * 0.78, x + w * 0.5, y + h)


def draw_scarf(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 0.85
    _path(
        c,
        [
            (x, y + h * 0.55),
            (x + w, y + h * 0.78),
            (x + w * 0.92, y + h * 0.38),
            (x + w * 0.08, y + h * 0.15),
        ],
        1.7,
    )
    ink(c, 1.3)
    c.line(x + w * 0.12, y + h * 0.42, x + w * 0.88, y + h * 0.62)
    c.line(x + w * 0.16, y + h * 0.32, x + w * 0.84, y + h * 0.52)
    for i in range(3):
        c.line(x + i * w * 0.06, y + h * 0.22, x + i * w * 0.06 - 4, y)


def draw_basket(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 0.85
    _path(
        c,
        [
            (x + w * 0.08, y + h * 0.55),
            (x + w * 0.92, y + h * 0.55),
            (x + w * 0.82, y),
            (x + w * 0.18, y),
        ],
        1.7,
    )
    ink(c, 1.7)
    c.arc(x + w * 0.12, y + h * 0.35, x + w * 0.88, y + h * 1.05, 0, 180)
    c.setLineWidth(1.2)
    c.line(x + w * 0.22, y + h * 0.12, x + w * 0.78, y + h * 0.12)
    c.line(x + w * 0.18, y + h * 0.28, x + w * 0.82, y + h * 0.28)
    c.line(x + w * 0.14, y + h * 0.42, x + w * 0.86, y + h * 0.42)


def draw_bible(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 0.78
    rect(c, x, y, w, h, 1.7)
    ink(c, 1.4)
    c.line(x + w * 0.12, y + 3, x + w * 0.12, y + h - 3)
    draw_cross(c, x + w * 0.58, y + h * 0.18, h * 0.52, width=1.6)


def draw_tree(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    trunk_w = w * 0.14
    rect(c, x + w * 0.43, y, trunk_w, h * 0.46, 1.7)
    # canopy as overlapping closed masses, not a single clip-art lollipop
    circle(c, x + w * 0.50, y + h * 0.70, w * 0.32, 1.8)
    circle(c, x + w * 0.32, y + h * 0.58, w * 0.24, 1.7)
    circle(c, x + w * 0.68, y + h * 0.58, w * 0.24, 1.7)
    circle(c, x + w * 0.50, y + h * 0.50, w * 0.22, 1.6)


def draw_child(
    c: canvas.Canvas,
    cx: float,
    foot_y: float,
    height: float,
    *,
    facing: int = 1,
    hair: str = "bob",
    lantern: bool = True,
) -> None:
    """Coloring-book child with mitten hands and a clearly held lantern."""
    head_r = height * 0.13
    head_cy = foot_y + height - head_r
    body_top = head_cy - head_r * 0.85
    body_h = height * 0.42
    body_w = height * 0.28
    # shoes + legs meet the clothing hem
    leg_top = body_top - body_h + height * 0.02
    rect(c, cx - height * 0.12, foot_y + height * 0.05, height * 0.09, leg_top - (foot_y + height * 0.05), 1.7)
    rect(c, cx + height * 0.03, foot_y + height * 0.05, height * 0.09, leg_top - (foot_y + height * 0.05), 1.7)
    oval(c, cx - height * 0.15, foot_y, cx - height * 0.01, foot_y + height * 0.07, 1.6)
    oval(c, cx + height * 0.01, foot_y, cx + height * 0.15, foot_y + height * 0.07, 1.6)
    if hair == "bob":
        _path(
            c,
            [
                (cx - body_w * 0.28, body_top),
                (cx + body_w * 0.28, body_top),
                (cx + body_w * 0.55, body_top - body_h),
                (cx - body_w * 0.55, body_top - body_h),
            ],
            1.9,
        )
    else:
        rect(c, cx - body_w * 0.42, body_top - body_h, body_w * 0.84, body_h, 1.9)

    # Outer-hand lantern so two facing children do not merge into one lamp.
    lantern_side = -facing
    shoulder_y = body_top - body_h * 0.18
    # hanging inner arm
    oval(
        c,
        cx + facing * height * 0.02,
        shoulder_y - height * 0.22,
        cx + facing * height * 0.16,
        shoulder_y + height * 0.04,
        1.6,
    )
    # lantern arm
    hand_x = cx + lantern_side * height * 0.28
    hand_y = shoulder_y - height * 0.06
    oval(
        c,
        min(cx, hand_x) - height * 0.02,
        hand_y - height * 0.05,
        max(cx, hand_x) + height * 0.02,
        shoulder_y + height * 0.04,
        1.6,
    )
    oval(c, hand_x - height * 0.05, hand_y - height * 0.05, hand_x + height * 0.05, hand_y + height * 0.05, 1.6)
    if lantern:
        draw_lantern(c, hand_x - height * 0.08, hand_y - height * 0.30, height * 0.30)

    if hair == "bob":
        oval(c, cx - head_r * 1.12, head_cy - head_r * 0.15, cx + head_r * 1.12, head_cy + head_r * 1.2, 1.8)
    else:
        oval(c, cx - head_r * 1.02, head_cy + head_r * 0.2, cx + head_r * 1.02, head_cy + head_r * 1.12, 1.8)
    circle(c, cx, head_cy, head_r, 1.9)
    ink(c, 1.3)
    c.setFillColor(black)
    c.circle(cx - head_r * 0.32, head_cy + head_r * 0.1, max(1.3, head_r * 0.07), fill=1, stroke=0)
    c.circle(cx + head_r * 0.32, head_cy + head_r * 0.1, max(1.3, head_r * 0.07), fill=1, stroke=0)
    c.setFillColor(white)
    c.setStrokeColor(black)
    c.arc(cx - head_r * 0.28, head_cy - head_r * 0.42, cx + head_r * 0.28, head_cy + head_r * 0.08, 200, 140)


def draw_church(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    body_h = h * 0.52
    rect(c, x + w * 0.08, y, w * 0.84, body_h, 2.0)
    _path(
        c,
        [
            (x, y + body_h),
            (x + w * 0.5, y + body_h + h * 0.18),
            (x + w, y + body_h),
        ],
        2.0,
    )
    tower_x = x + w * 0.40
    tower_w = w * 0.20
    tower_top = y + h * 0.82
    rect(c, tower_x, y + body_h * 0.55, tower_w, tower_top - (y + body_h * 0.55), 1.8)
    _path(
        c,
        [
            (tower_x - w * 0.04, tower_top),
            (tower_x + tower_w / 2, y + h * 0.94),
            (tower_x + tower_w + w * 0.04, tower_top),
        ],
        1.8,
    )
    draw_cross(c, tower_x + tower_w / 2, y + h * 0.90, h * 0.10, width=1.8)
    # door
    ink(c, 1.6)
    c.roundRect(x + w * 0.42, y, w * 0.16, body_h * 0.42, 8, fill=1, stroke=1)
    # arched windows
    for wx in (x + w * 0.18, x + w * 0.66):
        c.roundRect(wx, y + body_h * 0.28, w * 0.12, body_h * 0.38, 6, fill=1, stroke=1)
        c.arc(wx, y + body_h * 0.48, wx + w * 0.12, y + body_h * 0.78, 0, 180)


def draw_table(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    rect(c, x, y + h * 0.55, w, h * 0.18, 1.7)
    rect(c, x + w * 0.08, y, w * 0.08, h * 0.55, 1.5)
    rect(c, x + w * 0.84, y, w * 0.08, h * 0.55, 1.5)
    # pitcher and cups — closed, no text
    oval(c, x + w * 0.18, y + h * 0.68, x + w * 0.38, y + h * 0.92, 1.4)
    circle(c, x + w * 0.52, y + h * 0.78, h * 0.10, 1.3)
    circle(c, x + w * 0.70, y + h * 0.78, h * 0.10, 1.3)


def draw_string_lights(c: canvas.Canvas, x0: float, y0: float, x1: float, y1: float, bulbs: int = 7) -> None:
    ink(c, 1.3)
    mid_x = (x0 + x1) / 2
    sag = min(y0, y1) - abs(x1 - x0) * 0.12
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.curveTo(mid_x, sag, mid_x, sag, x1, y1)
    c.drawPath(p, fill=0, stroke=1)
    for i in range(bulbs):
        t = (i + 0.5) / bulbs
        bx = x0 * (1 - t) + x1 * t
        by = (1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * sag + t * t * y1
        oval(c, bx - 4, by - 10, bx + 4, by + 2, 1.2)


def draw_ground(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    _path(
        c,
        [
            (x, y),
            (x + w, y),
            (x + w, y + h * 0.85),
            (x + w * 0.62, y + h),
            (x + w * 0.28, y + h * 0.90),
            (x, y + h * 0.72),
        ],
        1.6,
    )


def draw_path(c: canvas.Canvas, points: list[tuple[float, float]], width: float) -> None:
    if len(points) < 2:
        return
    ink(c, 1.5)
    p = c.beginPath()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    c.drawPath(p, fill=0, stroke=1)
    # second parallel edge
    p2 = c.beginPath()
    p2.moveTo(points[0][0] + width, points[0][1])
    for pt in points[1:]:
        p2.lineTo(pt[0] + width, pt[1])
    c.drawPath(p2, fill=0, stroke=1)


def draw_cloud(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 0.42
    circle(c, x + w * 0.30, y + h * 0.45, h * 0.42, 1.4)
    circle(c, x + w * 0.52, y + h * 0.55, h * 0.48, 1.4)
    circle(c, x + w * 0.72, y + h * 0.42, h * 0.38, 1.4)


def draw_hedge_leaf_tuft(c: canvas.Canvas, x: float, y: float, s: float) -> None:
    circle(c, x, y, s, 1.1)
    circle(c, x + s * 0.7, y + s * 0.2, s * 0.7, 1.1)


def draw_heart(c: canvas.Canvas, cx: float, cy: float, s: float) -> None:
    circle(c, cx - s * 0.28, cy + s * 0.12, s * 0.30, 1.5)
    circle(c, cx + s * 0.28, cy + s * 0.12, s * 0.30, 1.5)
    _path(
        c,
        [
            (cx - s * 0.55, cy + s * 0.05),
            (cx, cy - s * 0.55),
            (cx + s * 0.55, cy + s * 0.05),
        ],
        1.5,
    )


def draw_lantern_post(c: canvas.Canvas, x: float, y: float, h: float) -> None:
    rect(c, x - 3, y, 6, h * 0.72, 1.5)
    draw_lantern(c, x - h * 0.10, y + h * 0.62, h * 0.38)


def draw_sun(c: canvas.Canvas, cx: float, cy: float, r: float) -> None:
    circle(c, cx, cy, r, 1.8)
    ink(c, 1.4)
    for i in range(8):
        ang = i * 45
        rad = math.radians(ang)
        c.line(
            cx + r * 1.15 * math.cos(rad),
            cy + r * 1.15 * math.sin(rad),
            cx + r * 1.45 * math.cos(rad),
            cy + r * 1.45 * math.sin(rad),
        )


def draw_moon(c: canvas.Canvas, cx: float, cy: float, r: float) -> None:
    circle(c, cx, cy, r, 1.7)
    ink(c, 1.7)
    c.setFillColor(white)
    c.circle(cx + r * 0.35, cy + r * 0.1, r * 0.78, fill=1, stroke=0)
    c.setStrokeColor(black)
    c.circle(cx, cy, r, fill=0, stroke=1)


def draw_star(c: canvas.Canvas, cx: float, cy: float, r: float) -> None:
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    _path(c, pts, 1.5)


def draw_barn(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    rect(c, x + w * 0.06, y, w * 0.88, h * 0.62, 2.0)
    _path(
        c,
        [
            (x, y + h * 0.62),
            (x + w * 0.5, y + h * 0.98),
            (x + w, y + h * 0.62),
        ],
        2.0,
    )
    ink(c, 1.6)
    c.roundRect(x + w * 0.38, y, w * 0.24, h * 0.38, 6, fill=1, stroke=1)
    c.line(x + w * 0.5, y, x + w * 0.5, y + h * 0.38)
    for wx in (x + w * 0.16, x + w * 0.70):
        c.roundRect(wx, y + h * 0.28, w * 0.12, h * 0.18, 4, fill=1, stroke=1)


def draw_wagon(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    rect(c, x + w * 0.08, y + h * 0.32, w * 0.84, h * 0.38, 1.8)
    circle(c, x + w * 0.26, y + h * 0.22, h * 0.20, 1.7)
    circle(c, x + w * 0.74, y + h * 0.22, h * 0.20, 1.7)
    rect(c, x + w * 0.78, y + h * 0.48, w * 0.18, h * 0.08, 1.4)


def draw_porch(c: canvas.Canvas, x: float, y: float, w: float, h: float, *, lit: bool = True) -> None:
    rect(c, x + w * 0.12, y + h * 0.18, w * 0.76, h * 0.70, 2.0)
    _path(
        c,
        [(x, y + h * 0.88), (x + w * 0.5, y + h), (x + w, y + h * 0.88)],
        1.8,
    )
    rect(c, x + w * 0.02, y + h * 0.18, w * 0.08, h * 0.70, 1.5)
    rect(c, x + w * 0.90, y + h * 0.18, w * 0.08, h * 0.70, 1.5)
    ink(c, 1.6)
    c.roundRect(x + w * 0.38, y + h * 0.18, w * 0.24, h * 0.42, 8, fill=1, stroke=1)
    if lit:
        oval(c, x + w * 0.22, y + h * 0.52, x + w * 0.34, y + h * 0.70, 1.4)
        oval(c, x + w * 0.66, y + h * 0.52, x + w * 0.78, y + h * 0.70, 1.4)


def draw_deer(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    oval(c, x + w * 0.18, y + h * 0.28, x + w * 0.78, y + h * 0.62, 1.7)
    circle(c, x + w * 0.78, y + h * 0.70, w * 0.12, 1.6)
    rect(c, x + w * 0.26, y, w * 0.08, h * 0.32, 1.4)
    rect(c, x + w * 0.42, y, w * 0.08, h * 0.30, 1.4)
    rect(c, x + w * 0.56, y, w * 0.08, h * 0.32, 1.4)
    rect(c, x + w * 0.68, y, w * 0.08, h * 0.30, 1.4)
    ink(c, 1.5)
    c.line(x + w * 0.78, y + h * 0.80, x + w * 0.70, y + h * 0.98)
    c.line(x + w * 0.82, y + h * 0.80, x + w * 0.88, y + h * 0.96)
    c.line(x + w * 0.70, y + h * 0.98, x + w * 0.66, y + h * 0.88)
    c.line(x + w * 0.88, y + h * 0.96, x + w * 0.92, y + h * 0.86)


def draw_chair(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    rect(c, x + w * 0.12, y + h * 0.38, w * 0.76, h * 0.12, 1.6)
    rect(c, x + w * 0.16, y, w * 0.10, h * 0.38, 1.5)
    rect(c, x + w * 0.74, y, w * 0.10, h * 0.38, 1.5)
    rect(c, x + w * 0.18, y + h * 0.48, w * 0.64, h * 0.46, 1.6)


def draw_booth(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    rect(c, x + w * 0.08, y, w * 0.84, h * 0.42, 1.8)
    _path(
        c,
        [(x, y + h * 0.42), (x + w * 0.5, y + h * 0.78), (x + w, y + h * 0.42)],
        1.8,
    )
    rect(c, x + w * 0.18, y + h * 0.08, w * 0.28, h * 0.18, 1.4)
    circle(c, x + w * 0.68, y + h * 0.22, w * 0.08, 1.4)


def draw_creek(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    ink(c, 1.6)
    p = c.beginPath()
    p.moveTo(x, y + h * 0.35)
    p.curveTo(x + w * 0.25, y + h * 0.05, x + w * 0.55, y + h * 0.70, x + w, y + h * 0.40)
    c.drawPath(p, fill=0, stroke=1)
    p2 = c.beginPath()
    p2.moveTo(x, y + h * 0.62)
    p2.curveTo(x + w * 0.30, y + h * 0.40, x + w * 0.60, y + h * 0.90, x + w, y + h * 0.70)
    c.drawPath(p2, fill=0, stroke=1)


def draw_loaf(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    oval(c, x, y, x + w, y + w * 0.55, 1.6)
    ink(c, 1.2)
    c.arc(x + w * 0.18, y + w * 0.18, x + w * 0.42, y + w * 0.48, 200, 140)
    c.arc(x + w * 0.42, y + w * 0.18, x + w * 0.66, y + w * 0.48, 200, 140)


def draw_wheat(c: canvas.Canvas, x: float, y: float, h: float) -> None:
    ink(c, 1.5)
    c.line(x, y, x, y + h)
    for i in range(5):
        yy = y + h * (0.45 + i * 0.10)
        c.line(x, yy, x - h * 0.12, yy + h * 0.04)
        c.line(x, yy, x + h * 0.12, yy + h * 0.04)
    oval(c, x - h * 0.06, y + h * 0.82, x + h * 0.06, y + h, 1.3)


def draw_window(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    rect(c, x, y, w, h, 1.7)
    ink(c, 1.3)
    c.line(x + w / 2, y, x + w / 2, y + h)
    c.line(x, y + h / 2, x + w, y + h / 2)
