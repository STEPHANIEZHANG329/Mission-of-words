"""KDP geometry, facing-page parity, and print-space Search & Find placement."""

from __future__ import annotations

from typing import Any, Iterable

from reportlab.lib.units import inch

TRIM_INCHES = (8.5, 11.0)
DPI = 300
SAFE_MARGIN_INCHES = 0.50
INNER_MARGIN_INCHES = 0.50  # gutter / binding edge
OUTER_MARGIN_INCHES = 0.50
TOP_MARGIN_INCHES = 0.50
BOTTOM_MARGIN_INCHES = 0.50
MIN_INSTRUCTION_PT = 12
MIN_PUZZLE_LETTER_PT = 12
MIN_ANSWER_KEY_PT = 9

PAGE_W = TRIM_INCHES[0] * inch
PAGE_H = TRIM_INCHES[1] * inch
MARGIN = SAFE_MARGIN_INCHES * inch

# Font sizes actually used by the deterministic builder. QA compares these
# against the floors above; they must never be lowered without a QA failure.
USED_INSTRUCTION_PT = 12
USED_PUZZLE_LETTER_PT = 12
USED_ANSWER_KEY_PT = 9
USED_TITLE_PT = 20

SEARCH_SCENE_LEFT_INSET_PT = 20
SEARCH_SCENE_RIGHT_INSET_PT = 20
SEARCH_SCENE_BOTTOM_INSET_PT = 95
SEARCH_SCENE_TOP_INSET_PT = 60
SEARCH_FIND_PAGE = 2
MIN_TARGET_PT = 18


def layout_metrics() -> dict:
    return {
        "trim_inches": list(TRIM_INCHES),
        "dpi": DPI,
        "safe_margin_inches": SAFE_MARGIN_INCHES,
        "inner_margin_inches": INNER_MARGIN_INCHES,
        "outer_margin_inches": OUTER_MARGIN_INCHES,
        "top_margin_inches": TOP_MARGIN_INCHES,
        "bottom_margin_inches": BOTTOM_MARGIN_INCHES,
        "min_instruction_pt": MIN_INSTRUCTION_PT,
        "min_puzzle_letter_pt": MIN_PUZZLE_LETTER_PT,
        "min_answer_key_pt": MIN_ANSWER_KEY_PT,
        "used_instruction_pt": USED_INSTRUCTION_PT,
        "used_puzzle_letter_pt": USED_PUZZLE_LETTER_PT,
        "used_answer_key_pt": USED_ANSWER_KEY_PT,
    }


def page_geometry(page_number: int, *, inner_inches: float | None = None, outer_inches: float | None = None) -> dict[str, Any]:
    """Return facing-page safe-area geometry in inches and PDF points."""
    inner = INNER_MARGIN_INCHES if inner_inches is None else float(inner_inches)
    outer = OUTER_MARGIN_INCHES if outer_inches is None else float(outer_inches)
    odd = page_number % 2 == 1
    left_in = inner if odd else outer
    right_in = outer if odd else inner
    left_pt = left_in * inch
    right_pt = right_in * inch
    top_pt = TOP_MARGIN_INCHES * inch
    bottom_pt = BOTTOM_MARGIN_INCHES * inch
    ok = (
        inner >= SAFE_MARGIN_INCHES
        and outer >= SAFE_MARGIN_INCHES
        and TOP_MARGIN_INCHES >= SAFE_MARGIN_INCHES
        and BOTTOM_MARGIN_INCHES >= SAFE_MARGIN_INCHES
    )
    return {
        "page": page_number,
        "side": "recto" if odd else "verso",
        "inner_edge": "left" if odd else "right",
        "outer_edge": "right" if odd else "left",
        "inner_inches": inner,
        "outer_inches": outer,
        "top_inches": TOP_MARGIN_INCHES,
        "bottom_inches": BOTTOM_MARGIN_INCHES,
        "left_inches": left_in,
        "right_inches": right_in,
        "left_pt": left_pt,
        "right_pt": right_pt,
        "top_pt": top_pt,
        "bottom_pt": bottom_pt,
        "safe_x0": left_pt,
        "safe_y0": bottom_pt,
        "safe_x1": PAGE_W - right_pt,
        "safe_y1": PAGE_H - top_pt,
        "ok": ok,
    }


def facing_page_report(*, inner_inches: float | None = None, outer_inches: float | None = None, page_count: int = 4) -> dict[str, Any]:
    pages = [page_geometry(number, inner_inches=inner_inches, outer_inches=outer_inches) for number in range(1, page_count + 1)]
    return {"ok": all(page["ok"] for page in pages), "pages": pages}


def search_find_scene_rect(page_number: int = SEARCH_FIND_PAGE, **margin_overrides: float | None) -> dict[str, float]:
    geo = page_geometry(page_number, **margin_overrides)
    x = geo["safe_x0"] + SEARCH_SCENE_LEFT_INSET_PT
    y = geo["safe_y0"] + SEARCH_SCENE_BOTTOM_INSET_PT
    w = (geo["safe_x1"] - geo["safe_x0"]) - SEARCH_SCENE_LEFT_INSET_PT - SEARCH_SCENE_RIGHT_INSET_PT
    h = (geo["safe_y1"] - geo["safe_y0"]) - SEARCH_SCENE_BOTTOM_INSET_PT - SEARCH_SCENE_TOP_INSET_PT
    return {"page": page_number, "x_pt": x, "y_pt": y, "width_pt": w, "height_pt": h, **geo}


def _boxes_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


def search_find_print_space(
    targets: Iterable[dict[str, Any]],
    page_number: int = SEARCH_FIND_PAGE,
    **margin_overrides: float | None,
) -> dict[str, Any]:
    """Place Search & Find targets in final PDF/print space (points) and 300 DPI composed pixels.

    Spec-space ratios are inputs only. QA uses the composed/print rectangles.
    """
    scene = search_find_scene_rect(page_number, **margin_overrides)
    scene_box = (
        scene["x_pt"],
        scene["y_pt"],
        scene["x_pt"] + scene["width_pt"],
        scene["y_pt"] + scene["height_pt"],
    )
    safe_box = (scene["safe_x0"], scene["safe_y0"], scene["safe_x1"], scene["safe_y1"])
    width_px = max(1, round(scene["width_pt"] * DPI / 72.0))
    height_px = max(1, round(scene["height_pt"] * DPI / 72.0))
    placed: list[dict[str, Any]] = []
    defects: list[str] = []

    for target in targets:
        name = str(target.get("name"))
        x_ratio = float(target["x"])
        y_ratio = float(target["y"])
        scale = float(target["scale"])
        size_pt = max(MIN_TARGET_PT, scene["width_pt"] * scale)
        x_pt = scene["x_pt"] + x_ratio * (scene["width_pt"] - size_pt)
        y_pt = scene["y_pt"] + y_ratio * (scene["height_pt"] - size_pt)
        box = (x_pt, y_pt, x_pt + size_pt, y_pt + size_pt)
        inside_scene = box[0] >= scene_box[0] - 0.01 and box[1] >= scene_box[1] - 0.01 and box[2] <= scene_box[2] + 0.01 and box[3] <= scene_box[3] + 0.01
        inside_safe = box[0] >= safe_box[0] and box[1] >= safe_box[1] and box[2] <= safe_box[2] and box[3] <= safe_box[3]
        if not inside_scene or not inside_safe:
            defects.append(f"search_find print-space: {name} is outside the page-2 safe/composed scene")

        # Composed canvas uses top-left origin, matching compositor.py.
        width_ratio = size_pt / scene["width_pt"]
        target_width_px = max(1, round(width_px * width_ratio))
        target_height_px = target_width_px
        x_px = round((width_px - target_width_px) * x_ratio)
        y_px_from_bottom = (y_pt - scene["y_pt"]) * DPI / 72.0
        y_px = round(height_px - y_px_from_bottom - target_height_px)
        pixel_box = (x_px, y_px, x_px + target_width_px, y_px + target_height_px)
        if x_px < 0 or y_px < 0 or x_px + target_width_px > width_px or y_px + target_height_px > height_px:
            defects.append(f"search_find composed-space: {name} clips the 300 DPI scene")

        placed.append(
            {
                "name": name,
                "x_pt": x_pt,
                "y_pt": y_pt,
                "width_pt": size_pt,
                "height_pt": size_pt,
                "x_in": x_pt / inch,
                "y_in": y_pt / inch,
                "x_px": x_px,
                "y_px": y_px,
                "width_px": target_width_px,
                "height_px": target_height_px,
                "inside_safe_rect": inside_safe,
                "inside_scene": inside_scene,
            }
        )
        _ = pixel_box

    overlap = False
    for index, left in enumerate(placed):
        box_a = (left["x_pt"], left["y_pt"], left["x_pt"] + left["width_pt"], left["y_pt"] + left["height_pt"])
        for right in placed[index + 1 :]:
            box_b = (right["x_pt"], right["y_pt"], right["x_pt"] + right["width_pt"], right["y_pt"] + right["height_pt"])
            if _boxes_overlap(box_a, box_b):
                overlap = True
                defects.append(f"search_find print-space: unsafe overlap between {left['name']} and {right['name']}")

    return {
        "ok": not defects,
        "scene_pt": {"x": scene["x_pt"], "y": scene["y_pt"], "width": scene["width_pt"], "height": scene["height_pt"]},
        "composed_px": {"width": width_px, "height": height_px, "dpi": DPI},
        "targets": placed,
        "all_inside_safe_rect": all(item["inside_safe_rect"] for item in placed) if placed else False,
        "no_unsafe_overlap": not overlap,
        "defects": defects,
    }
