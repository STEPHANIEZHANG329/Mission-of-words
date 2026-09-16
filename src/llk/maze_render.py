"""Rasterize maze walls so tests can prove START/FINISH gaps exist in pixels."""

from __future__ import annotations

from PIL import Image, ImageDraw

from llk.maze import Maze, opening_edges, wall_segments


def render_maze_bitmap(maze: Maze, *, cell: int = 24, stroke: int = 3) -> Image.Image:
    pad = stroke + 4
    w = maze.cols * cell + pad * 2
    h = maze.rows * cell + pad * 2
    img = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(img)

    def xy(x: float, y: float) -> tuple[int, int]:
        return int(round(pad + x * cell)), int(round(pad + y * cell))

    for x1, y1, x2, y2 in wall_segments(maze):
        draw.line([xy(x1, y1), xy(x2, y2)], fill=0, width=stroke)
    return img


def _edge_ink_ratio(img: Image.Image, maze: Maze, edge: tuple[float, float, float, float], *, cell: int = 24, stroke: int = 3) -> float:
    pad = stroke + 4
    x1, y1, x2, y2 = edge
    # Sample the inner 50% of the edge so corner joints do not count as a closed wall.
    mx1 = x1 + (x2 - x1) * 0.25
    my1 = y1 + (y2 - y1) * 0.25
    mx2 = x1 + (x2 - x1) * 0.75
    my2 = y1 + (y2 - y1) * 0.75
    px1 = int(round(pad + mx1 * cell))
    py1 = int(round(pad + my1 * cell))
    px2 = int(round(pad + mx2 * cell))
    py2 = int(round(pad + my2 * cell))
    band = max(1, stroke)
    x0, x1b = sorted((px1, px2))
    y0, y1b = sorted((py1, py2))
    crop = img.crop((x0 - band, y0 - band, x1b + band + 1, y1b + band + 1))
    pixels = list(crop.getdata())
    if not pixels:
        return 1.0
    ink = sum(1 for p in pixels if p < 80)
    return ink / len(pixels)


def assert_physical_openings(maze: Maze) -> dict[str, float]:
    """Fail unless START/FINISH outer walls are actual gaps in the rendered maze."""
    cell, stroke = 24, 3
    img = render_maze_bitmap(maze, cell=cell, stroke=stroke)
    openings = opening_edges(maze)
    start_ink = _edge_ink_ratio(img, maze, openings["start"], cell=cell, stroke=stroke)
    finish_ink = _edge_ink_ratio(img, maze, openings["finish"], cell=cell, stroke=stroke)
    if start_ink > 0.18:
        raise AssertionError(f"START opening is closed (ink ratio {start_ink:.2f})")
    if finish_ink > 0.18:
        raise AssertionError(f"FINISH opening is closed (ink ratio {finish_ink:.2f})")
    # A known closed outer wall (west wall of start) must still be inked.
    sc, sr = maze.start
    closed = _edge_ink_ratio(img, maze, (sc, sr, sc, sr + 1), cell=cell, stroke=stroke)
    if closed < 0.20:
        raise AssertionError(f"expected a closed west wall at start, ink ratio {closed:.2f}")
    return {"start_ink": start_ink, "finish_ink": finish_ink, "closed_west_ink": closed}
