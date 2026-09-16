"""Ink-aware Search & Find placement. Reuses target sheets; never calls the image API."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageFilter

from llk.spec import Target


@dataclass(frozen=True)
class PlacedTarget:
    name: str
    x: float  # 0-1 in the fitted image rectangle, top-left
    y: float
    scale: float


def _cost_grid(bg: Image.Image, cells: int = 36) -> list[list[float]]:
    gray = bg.convert("L").resize((cells, cells), Image.Resampling.BOX)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    gp = gray.load()
    ep = edges.load()
    grid: list[list[float]] = []
    for y in range(cells):
        row = []
        for x in range(cells):
            ink = (255 - gp[x, y]) / 255.0
            edge = ep[x, y] / 255.0
            # Faces, hands, and major contours are dark and/or high-edge.
            row.append(ink * 1.35 + edge * 1.6)
        grid.append(row)
    return grid


def _block_cost(grid: list[list[float]], x0: float, y0: float, x1: float, y1: float) -> float:
    cells = len(grid)
    c0 = max(0, int(x0 * cells))
    r0 = max(0, int(y0 * cells))
    c1 = min(cells, int(x1 * cells) + 1)
    r1 = min(cells, int(y1 * cells) + 1)
    if c1 <= c0 or r1 <= r0:
        return 9.0
    total = 0.0
    n = 0
    for r in range(r0, r1):
        for c in range(c0, c1):
            total += grid[r][c]
            n += 1
    return total / max(n, 1)


def _overlap(a: PlacedTarget, b: PlacedTarget) -> bool:
    aw, ah = a.scale, a.scale * 1.05
    bw, bh = b.scale, b.scale * 1.05
    return not (a.x + aw <= b.x or b.x + bw <= a.x or a.y + ah <= b.y or b.y + bh <= a.y)


def place_targets(bg: Image.Image, targets: tuple[Target, ...] | list[Target]) -> list[PlacedTarget]:
    """Move targets off faces/hands/heavy contours while keeping 8 unique finds."""
    grid = _cost_grid(bg)
    placed: list[PlacedTarget] = []
    # Slightly smaller so icons sit in the scene instead of floating as stickers.
    for target in targets:
        scale = min(max(target.scale * 0.88, 0.072), 0.11)
        candidates: list[tuple[float, float]] = [(target.x, target.y)]
        # Spiral / jitter around the authored point, then a coarse global scan.
        for rad in (0.06, 0.12, 0.20, 0.30):
            for dx, dy in (
                (rad, 0),
                (-rad, 0),
                (0, rad),
                (0, -rad),
                (rad, rad),
                (-rad, rad),
                (rad, -rad),
                (-rad, -rad),
                (rad * 0.5, rad),
                (-rad * 0.5, -rad),
            ):
                candidates.append((target.x + dx, target.y + dy))
        for gy in range(8, 90, 7):
            for gx in range(6, 88, 8):
                candidates.append((gx / 100.0, gy / 100.0))
        best: PlacedTarget | None = None
        best_cost = 1e9
        for cx, cy in candidates:
            cx = min(max(cx, 0.03), 0.97 - scale)
            cy = min(max(cy, 0.08), 0.94 - scale)
            trial = PlacedTarget(target.name, cx, cy, scale)
            if any(_overlap(trial, p) for p in placed):
                continue
            cost = _block_cost(grid, cx, cy, cx + scale, cy + scale)
            # Prefer staying near the authored point if the region is already quiet.
            dist = abs(cx - target.x) + abs(cy - target.y)
            score = cost + dist * 0.15
            if score < best_cost:
                best_cost = score
                best = trial
        if best is None:
            best = PlacedTarget(target.name, min(max(target.x, 0.04), 0.86), min(max(target.y, 0.12), 0.84), scale)
        placed.append(best)
    return placed
