"""Search & Find difficulty rules for ages 5–8.

Placement uses compositor semantics: x_ratio/y_ratio are fractions of the
remaining space after the target size is reserved, so a ratio of 1.0 sits
flush to the far edge without clipping.
"""

from __future__ import annotations

from typing import Any, Iterable

# Ages 5-8: readable but not giant clip-art. Ladybug at 0.07 is the floor
# already used by Mission 7; nothing may go smaller.
MIN_WIDTH_RATIO = 0.07
MAX_WIDTH_RATIO = 0.14
# Keep hunt objects inside the live scene, away from trim crop.
EDGE_INSET_RATIO = 0.015
# Boxes may not overlap; a small gap keeps occlusion from hiding a target.
MIN_GAP_RATIO = 0.003
# Centers should not pile into one empty corner.
MAX_TARGETS_PER_CORNER = 3
CORNER_SPAN = 0.32


def _box(x_ratio: float, y_ratio: float, width_ratio: float) -> tuple[float, float, float, float]:
    left = (1.0 - width_ratio) * x_ratio
    top = (1.0 - width_ratio) * y_ratio
    return left, top, left + width_ratio, top + width_ratio


def _overlap_area(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    return (ix1 - ix0) * (iy1 - iy0)


def _gap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> float:
    if _overlap_area(a, b) > 0:
        return 0.0
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    dx = 0.0 if ax1 >= bx0 and bx1 >= ax0 else min(abs(ax1 - bx0), abs(bx1 - ax0))
    dy = 0.0 if ay1 >= by0 and by1 >= ay0 else min(abs(ay1 - by0), abs(by1 - ay0))
    if ax1 >= bx0 and bx1 >= ax0:
        return dy
    if ay1 >= by0 and by1 >= ay0:
        return dx
    return (dx**2 + dy**2) ** 0.5


def _corner(cx: float, cy: float) -> str | None:
    lo, hi = CORNER_SPAN, 1.0 - CORNER_SPAN
    if cx <= lo and cy <= lo:
        return "top_left"
    if cx >= hi and cy <= lo:
        return "top_right"
    if cx <= lo and cy >= hi:
        return "bottom_left"
    if cx >= hi and cy >= hi:
        return "bottom_right"
    return None


def evaluate_search_difficulty(
    targets: Iterable[dict[str, Any]],
    *,
    excluded_background_objects: Iterable[str] | None = None,
    owner: str = "search_find",
) -> list[str]:
    """Return fail-closed defects. Empty list means the hunt is legal for ages 5–8."""
    rows = list(targets)
    failures: list[str] = []
    names = [str(item.get("name") or "") for item in rows]
    if len(rows) != 8:
        failures.append(f"{owner}: expected 8 targets, got {len(rows)}")
        return failures
    if len(set(names)) != 8 or any(not name for name in names):
        failures.append(f"{owner}: targets must be eight unique names, got {names}")
        return failures

    boxes: list[tuple[str, tuple[float, float, float, float]]] = []
    corners: dict[str, list[str]] = {}
    for target in rows:
        name = str(target["name"])
        x = float(target["x"])
        y = float(target["y"])
        scale = float(target["scale"])
        if scale + 1e-12 < MIN_WIDTH_RATIO:
            failures.append(
                f"{owner}: {name} scale {scale:.3f} is below min {MIN_WIDTH_RATIO}"
            )
        if scale - 1e-12 > MAX_WIDTH_RATIO:
            failures.append(
                f"{owner}: {name} scale {scale:.3f} exceeds max {MAX_WIDTH_RATIO}"
            )
        box = _box(x, y, scale)
        left, top, right, bottom = box
        if left < EDGE_INSET_RATIO - 1e-9 or top < EDGE_INSET_RATIO - 1e-9:
            failures.append(f"{owner}: {name} violates edge safety (too close to origin)")
        if right > 1.0 - EDGE_INSET_RATIO + 1e-9 or bottom > 1.0 - EDGE_INSET_RATIO + 1e-9:
            failures.append(f"{owner}: {name} violates edge safety (too close to far edge)")
        boxes.append((name, box))
        cx, cy = (left + right) / 2, (top + bottom) / 2
        corner = _corner(cx, cy)
        if corner:
            corners.setdefault(corner, []).append(name)

    for index, (name_a, box_a) in enumerate(boxes):
        for name_b, box_b in boxes[index + 1 :]:
            overlap = _overlap_area(box_a, box_b)
            if overlap > 0:
                failures.append(
                    f"{owner}: unsafe overlap/occlusion between {name_a} and {name_b}"
                )
                continue
            if _gap(box_a, box_b) < MIN_GAP_RATIO:
                failures.append(
                    f"{owner}: {name_a} and {name_b} are closer than the minimum gap"
                )

    for corner, grouped in corners.items():
        if len(grouped) > MAX_TARGETS_PER_CORNER:
            failures.append(
                f"{owner}: {len(grouped)} targets clustered in empty {corner} corner: {grouped}"
            )

    excluded = {str(item) for item in (excluded_background_objects or [])}
    if excluded:
        missing = [name for name in names if name not in excluded]
        if missing:
            failures.append(
                f"{owner}: search background must exclude hunt targets {missing}"
            )
        # Ambiguity: background must not keep a hunt object as scenery.
        # The excluded list is the contract; extra names are allowed as clutter
        # only when they are not target names.
    return failures


def evaluate_composed_targets(
    manifest: Iterable[dict[str, Any]],
    *,
    scene_width_px: int,
    scene_height_px: int,
    owner: str = "search_find",
) -> list[str]:
    """Pixel-space difficulty checks on a compositor answer manifest."""
    failures: list[str] = []
    edge_x = max(1, round(scene_width_px * EDGE_INSET_RATIO))
    edge_y = max(1, round(scene_height_px * EDGE_INSET_RATIO))
    boxes: list[tuple[str, tuple[int, int, int, int]]] = []
    names: list[str] = []
    for row in manifest:
        name = str(row.get("name") or "")
        x = int(row["x"])
        y = int(row["y"])
        width = int(row["width"])
        height = int(row["height"])
        names.append(name)
        failures.extend(
            pixel_size_failures(
                name=name,
                width_px=width,
                height_px=height,
                scene_width_px=scene_width_px,
                scene_height_px=scene_height_px,
                owner=owner,
            )
        )
        if x < edge_x or y < edge_y or x + width > scene_width_px - edge_x or y + height > scene_height_px - edge_y:
            failures.append(f"{owner}: {name} violates pixel edge safety")
        boxes.append((name, (x, y, width, height)))
    if len(names) != 8 or len(set(names)) != 8:
        failures.append(f"{owner}: compositor manifest must contain 8 unique targets, got {names}")
    for index, (name_a, box_a) in enumerate(boxes):
        ax, ay, aw, ah = box_a
        for name_b, box_b in boxes[index + 1 :]:
            bx, by, bw, bh = box_b
            overlap = not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)
            if overlap:
                failures.append(f"{owner}: pixel occlusion between {name_a} and {name_b}")
    return failures


def pixel_size_failures(
    *,
    name: str,
    width_px: int,
    height_px: int,
    scene_width_px: int,
    scene_height_px: int,
    owner: str = "search_find",
) -> list[str]:
    failures: list[str] = []
    min_w = max(1, round(scene_width_px * MIN_WIDTH_RATIO))
    max_w = max(min_w, round(scene_width_px * MAX_WIDTH_RATIO))
    if width_px < min_w:
        failures.append(f"{owner}: {name} pixel width {width_px} is below min {min_w}")
    if width_px > max_w:
        failures.append(f"{owner}: {name} pixel width {width_px} exceeds max {max_w}")
    if height_px < 1 or width_px < 1:
        failures.append(f"{owner}: {name} has non-positive pixel size")
    return failures
