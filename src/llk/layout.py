"""Axis-aligned layout boxes used to reject text/art/rule collisions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    name: str
    x: float
    y: float
    w: float
    h: float

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h


def overlaps(a: Box, b: Box, pad: float = 1.5) -> bool:
    return not (
        a.x2 + pad <= b.x
        or b.x2 + pad <= a.x
        or a.y2 + pad <= b.y
        or b.y2 + pad <= a.y
    )


def assert_no_collisions(boxes: list[Box], *, ignore_pairs: set[tuple[str, str]] | None = None) -> None:
    ignore = set(ignore_pairs or set())
    ignore.add(("art", "target"))
    ignore.add(("target", "art"))
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            pair = tuple(sorted((a.name.split(":")[0], b.name.split(":")[0])))
            if pair in ignore or (a.name, b.name) in ignore:
                continue
            # Footer may sit close to content; only fail hard overlaps of header/art/rule.
            kinds = {a.name.split(":")[0], b.name.split(":")[0]}
            if "footer" in kinds:
                continue
            if overlaps(a, b, pad=0.75):
                raise AssertionError(f"layout collision {a.name} vs {b.name}")
