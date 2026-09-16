"""Deterministic perfect maze with a unique start-to-finish path."""

from __future__ import annotations

import random
from dataclasses import dataclass


N, E, S, W = 1, 2, 4, 8
DELTA = {N: (-1, 0), E: (0, 1), S: (1, 0), W: (0, -1)}
OPPOSITE = {N: S, E: W, S: N, W: E}


@dataclass(frozen=True)
class Maze:
    cols: int
    rows: int
    seed: int
    walls: tuple[tuple[int, ...], ...]  # bitfield of remaining walls per cell
    path: tuple[tuple[int, int], ...]  # (col, row) from start to end

    @property
    def start(self) -> tuple[int, int]:
        return (0, 0)

    @property
    def end(self) -> tuple[int, int]:
        return (self.cols - 1, self.rows - 1)


def generate_maze(cols: int, rows: int, seed: int) -> Maze:
    if cols < 4 or rows < 4:
        raise ValueError("maze too small for ages 5-8 print cells")
    rng = random.Random(seed)
    walls = [[N | E | S | W for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    def carve(c: int, r: int) -> None:
        visited[r][c] = True
        dirs = [N, E, S, W]
        rng.shuffle(dirs)
        for d in dirs:
            dr, dc = DELTA[d]
            nc, nr = c + dc, r + dr
            if 0 <= nc < cols and 0 <= nr < rows and not visited[nr][nc]:
                walls[r][c] &= ~d
                walls[nr][nc] &= ~OPPOSITE[d]
                carve(nc, nr)

    carve(0, 0)
    path = _unique_path(walls, cols, rows)
    return Maze(cols=cols, rows=rows, seed=seed, walls=tuple(tuple(row) for row in walls), path=tuple(path))


def _unique_path(walls: list[list[int]], cols: int, rows: int) -> list[tuple[int, int]]:
    start = (0, 0)
    end = (cols - 1, rows - 1)
    prev: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    queue = [start]
    while queue:
        c, r = queue.pop(0)
        if (c, r) == end:
            break
        for d, (dr, dc) in DELTA.items():
            if walls[r][c] & d:
                continue
            nxt = (c + dc, r + dr)
            if nxt in prev:
                continue
            nc, nr = nxt
            if 0 <= nc < cols and 0 <= nr < rows:
                prev[nxt] = (c, r)
                queue.append(nxt)
    if end not in prev:
        raise RuntimeError("maze is not solvable")
    # Confirm uniqueness of shortest/any path by counting paths with DFS cap.
    path: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    if not _has_unique_path(walls, cols, rows):
        raise RuntimeError("maze has multiple solutions")
    return path


def _has_unique_path(walls: list[list[int]], cols: int, rows: int) -> bool:
    end = (cols - 1, rows - 1)
    found = 0

    def dfs(c: int, r: int, seen: set[tuple[int, int]]) -> None:
        nonlocal found
        if found > 1:
            return
        if (c, r) == end:
            found += 1
            return
        for d, (dr, dc) in DELTA.items():
            if walls[r][c] & d:
                continue
            nxt = (c + dc, r + dr)
            if nxt in seen:
                continue
            nc, nr = nxt
            if 0 <= nc < cols and 0 <= nr < rows:
                seen.add(nxt)
                dfs(nc, nr, seen)
                seen.remove(nxt)

    dfs(0, 0, {(0, 0)})
    return found == 1


def neighbors_open(maze: Maze, c: int, r: int) -> list[tuple[int, int]]:
    out = []
    for d, (dr, dc) in DELTA.items():
        if maze.walls[r][c] & d:
            continue
        out.append((c + dc, r + dr))
    return out


def is_boundary_opening(maze: Maze, col: int, row: int, wall: int) -> bool:
    """True when this outer wall is the physical START or FINISH gap."""
    if (col, row) == maze.start and wall == N:
        return True
    if (col, row) == maze.end and wall == S:
        return True
    return False


def wall_segments(maze: Maze) -> list[tuple[float, float, float, float]]:
    """Axis-aligned wall segments in cell units, y growing downward, openings omitted.

    A segment is (x1, y1, x2, y2) where (0,0) is the top-left corner of the start cell.
    """
    segs: list[tuple[float, float, float, float]] = []
    for r in range(maze.rows):
        for c in range(maze.cols):
            bits = maze.walls[r][c]
            if bits & N and not is_boundary_opening(maze, c, r, N):
                segs.append((c, r, c + 1, r))
            if bits & E and not is_boundary_opening(maze, c, r, E):
                segs.append((c + 1, r, c + 1, r + 1))
            if bits & S and not is_boundary_opening(maze, c, r, S):
                segs.append((c, r + 1, c + 1, r + 1))
            if bits & W and not is_boundary_opening(maze, c, r, W):
                segs.append((c, r, c, r + 1))
    return segs


def opening_edges(maze: Maze) -> dict[str, tuple[float, float, float, float]]:
    """The omitted outer edges, in the same cell-unit space as wall_segments."""
    sc, sr = maze.start
    ec, er = maze.end
    return {
        "start": (sc, sr, sc + 1, sr),  # north edge of start
        "finish": (ec, er + 1, ec + 1, er + 1),  # south edge of finish
    }
