from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from random import Random
from typing import Dict, Iterable, List, Set, Tuple

Cell = Tuple[int, int]


@dataclass(frozen=True)
class Maze:
    rows: int
    cols: int
    passages: Dict[Cell, Set[Cell]]
    start: Cell
    finish: Cell

    def neighbors(self, cell: Cell) -> Iterable[Cell]:
        return self.passages[cell]

    def solve(self) -> List[Cell]:
        queue = deque([self.start])
        parent: Dict[Cell, Cell | None] = {self.start: None}
        while queue:
            current = queue.popleft()
            if current == self.finish:
                break
            for nxt in self.passages[current]:
                if nxt not in parent:
                    parent[nxt] = current
                    queue.append(nxt)
        if self.finish not in parent:
            raise ValueError("Maze is not solvable")
        path: List[Cell] = []
        cur: Cell | None = self.finish
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path

    def edge_count(self) -> int:
        return sum(len(v) for v in self.passages.values()) // 2

    def is_perfect(self) -> bool:
        # A connected graph with N-1 edges is a tree, therefore there is one
        # unique route between any pair of cells.
        if self.edge_count() != self.rows * self.cols - 1:
            return False
        visited = set()
        queue = deque([self.start])
        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            queue.extend(self.passages[cur] - visited)
        return len(visited) == self.rows * self.cols


def generate_maze(rows: int, cols: int, seed: int) -> Maze:
    if rows < 2 or cols < 2:
        raise ValueError("Maze must be at least 2x2")

    rng = Random(seed)
    passages: Dict[Cell, Set[Cell]] = {
        (r, c): set() for r in range(rows) for c in range(cols)
    }
    start = (0, 0)
    stack = [start]
    visited = {start}

    while stack:
        r, c = stack[-1]
        candidates = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nxt = (r + dr, c + dc)
            if 0 <= nxt[0] < rows and 0 <= nxt[1] < cols and nxt not in visited:
                candidates.append(nxt)
        if not candidates:
            stack.pop()
            continue

        nxt = rng.choice(candidates)
        passages[(r, c)].add(nxt)
        passages[nxt].add((r, c))
        visited.add(nxt)
        stack.append(nxt)

    maze = Maze(rows=rows, cols=cols, passages=passages, start=start, finish=(rows - 1, cols - 1))
    if not maze.is_perfect():
        raise AssertionError("Generated maze failed perfect-maze validation")
    return maze
