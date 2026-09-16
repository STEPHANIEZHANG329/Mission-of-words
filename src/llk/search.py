"""Search-and-find target placement rules."""

from __future__ import annotations

from llk.spec import TARGETS_PER_SEARCH, Mission, Target


def validate_targets(targets: tuple[Target, ...] | list[Target], *, page_label: str = "") -> None:
    if len(targets) != TARGETS_PER_SEARCH:
        raise ValueError(f"{page_label} expected {TARGETS_PER_SEARCH} targets, got {len(targets)}")
    names = [t.name for t in targets]
    if len(set(names)) != len(names):
        raise ValueError(f"{page_label} duplicate target names: {names}")
    boxes = []
    for t in targets:
        if not (0.02 <= t.x <= 0.90 and 0.08 <= t.y <= 0.90):
            raise ValueError(f"{page_label} target {t.name} out of bounds x={t.x} y={t.y}")
        if not (0.06 <= t.scale <= 0.16):
            raise ValueError(f"{page_label} target {t.name} scale {t.scale} not in 0.06-0.16")
        boxes.append((t.name, t.x, t.y, t.scale, t.x + t.scale, t.y + t.scale))
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            overlap_w = min(a[4], b[4]) - max(a[1], b[1])
            overlap_h = min(a[5], b[5]) - max(a[2], b[2])
            if overlap_w > 0 and overlap_h > 0:
                area = overlap_w * overlap_h
                if area > 0.012:
                    raise ValueError(f"{page_label} targets {a[0]} and {b[0]} overlap too much")


def validate_mission_search(mission: Mission) -> None:
    search = next(p for p in mission.pages if p.type == "search_find")
    validate_targets(search.targets, page_label=mission.id)
