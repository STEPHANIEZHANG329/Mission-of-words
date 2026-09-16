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
