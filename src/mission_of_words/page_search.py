"""Search & Find pages. Background and targets are independent assets."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words import procedural
from mission_of_words.compositor import AssetPlacement, compose_search_find
from mission_of_words.layout import DPI, USED_PUZZLE_LETTER_PT, content_box
from mission_of_words.paths import OUTPUT_DIR
from mission_of_words.proof import live_box
from mission_of_words.search_difficulty import evaluate_composed_targets, evaluate_search_difficulty
from mission_of_words.targets import display_name
from mission_of_words.text import ink_text, page_header

REQUIRED_TARGETS = (
    "lantern",
    "pumpkin",
    "apple",
    "leaf",
    "acorn",
    "scarf",
    "basket",
    "Bible",
)

LEGEND_H = 96
ICON_DRAWERS = {
    "lantern": lambda c, x, y: art.draw_lantern(c, x, y, 22),
    "pumpkin": lambda c, x, y: art.draw_pumpkin(c, x, y, 22),
    "apple": lambda c, x, y: art.draw_apple(c, x, y, 20),
    "leaf": lambda c, x, y: art.draw_leaf(c, x, y, 20),
    "acorn": lambda c, x, y: art.draw_acorn(c, x, y, 18),
    "scarf": lambda c, x, y: art.draw_scarf(c, x, y, 20),
    "basket": lambda c, x, y: art.draw_basket(c, x, y, 22),
    "Bible": lambda c, x, y: art.draw_bible(c, x, y, 22),
}


def _mission_from_spec(spec: dict) -> dict:
    if "mission" in spec and isinstance(spec["mission"], dict) and "pages" in spec["mission"]:
        return spec["mission"]
    return spec


def search_geometry(
    page_number: int, *, marked_proof: bool = False
) -> tuple[tuple[float, float, float, float], float]:
    box = live_box(page_number) if marked_proof else content_box(page_number)
    return box, LEGEND_H


def _scene_pixel_size(box: tuple[float, float, float, float], legend_h: float) -> tuple[int, int]:
    left, bottom, right, top = box
    width_in = (right - left) / 72.0
    height_in = (top - bottom - legend_h - 110) / 72.0
    return max(1, math.ceil(width_in * DPI) + 2), max(1, math.ceil(max(height_in, 1.0) * DPI) + 2)


def build_search_scene_from_page(
    search_page: dict,
    dest_dir: Path,
    *,
    page_number: int,
    theme: str,
    marked_proof: bool = False,
    status: str = "procedural_lineart",
    source: str = "procedural",
    store_root: Path | None = None,
) -> tuple[Path, list[dict], list[dict]]:
    box, legend_h = search_geometry(page_number, marked_proof=marked_proof)
    px_w, px_h = _scene_pixel_size(box, legend_h)
    dest_dir.mkdir(parents=True, exist_ok=True)
    bg_path = dest_dir / "search_background.png"
    targets = list(search_page["targets"])
    names = [str(target["name"]) for target in targets]
    difficulty_failures = evaluate_search_difficulty(
        targets,
        excluded_background_objects=names,
        owner=f"{theme} search_find",
    )
    if difficulty_failures:
        raise ValueError("; ".join(difficulty_failures))
    records: list[dict] = []
    placements: list[AssetPlacement] = []
    if source == "accepted":
        from mission_of_words.ingest import search_kit

        kit = search_kit(theme, store_root)
        Image.open(kit["background"].path).convert("RGB").save(bg_path)
        records.append(
            {
                "asset_id": kit["background"].asset_id,
                "role": "search_background",
                "status": "accepted",
                "file": str(kit["background"].path),
                "sha256": kit["background"].sha256,
                "paid_call": False,
                "cost_usd": 0.0,
            }
        )
        by_name = {t["name"]: t for t in targets}
        for name in names:
            loaded = kit["targets"][name]
            asset_path = dest_dir / f"target_{name}.png"
            Image.open(loaded.path).convert("RGBA").save(asset_path)
            records.append(
                {
                    "asset_id": loaded.asset_id,
                    "role": "search_target",
                    "status": "accepted",
                    "file": str(loaded.path),
                    "sha256": loaded.sha256,
                    "paid_call": False,
                    "cost_usd": 0.0,
                }
            )
            target = by_name[name]
            placements.append(
                AssetPlacement(
                    name=name,
                    asset_path=asset_path,
                    x_ratio=float(target["x"]),
                    y_ratio=float(target["y"]),
                    width_ratio=float(target["scale"]),
                )
            )
    else:
        bg_record = procedural.render_search_background(
            bg_path,
            px_w,
            px_h,
            theme=theme,
            status=status,
            excluded_targets=names,
        )
        records = [bg_record]
        by_name = {t["name"]: t for t in targets}
        for name in names:
            target = by_name[name]
            asset_path = dest_dir / f"target_{name}.png"
            records.append(procedural.render_target(name, asset_path, status=status))
            placements.append(
                AssetPlacement(
                    name=name,
                    asset_path=asset_path,
                    x_ratio=float(target["x"]),
                    y_ratio=float(target["y"]),
                    width_ratio=float(target["scale"]),
                )
            )
    composed = dest_dir / "search_composed.jpg"
    manifest = compose_search_find(bg_path, placements, composed)
    with Image.open(composed) as composed_image:
        scene_w, scene_h = composed_image.size
    composed_failures = evaluate_composed_targets(
        manifest,
        scene_width_px=scene_w,
        scene_height_px=scene_h,
        owner=f"{theme} search_find",
    )
    if composed_failures:
        raise ValueError("; ".join(composed_failures))
    return composed, manifest, records


def build_search_scene(spec: dict, dest_dir: Path) -> tuple[Path, list[dict], list[dict]]:
    mission = _mission_from_spec(spec)
    return build_search_scene_from_page(
        mission["pages"][1],
        dest_dir,
        page_number=2,
        theme=mission.get("id") or "mission_01",
        marked_proof=False,
        status="accepted",
    )


def draw_search_find_page(
    c: canvas.Canvas,
    spec: dict,
    composed_path: Path,
    manifest: list[dict],
    *,
    answer_key: bool = False,
    page_number: int | None = None,
    marked_proof: bool = False,
    icon_dir: Path | None = None,
    canon: dict | None = None,
) -> dict:
    mission = _mission_from_spec(spec)
    page = mission["pages"][1]
    number = page_number if page_number is not None else (2 if not answer_key else 1)
    reference = (canon or {}).get("reference") or mission.get("scripture_reference") or ""
    title = page["title"] if not answer_key else f"{page['title']} — Answer Key"
    instruction = (
        page["child_instruction"]
        if not answer_key
        else "Circles mark the same independently placed targets used on the child page."
    )
    box = live_box(number) if marked_proof else None
    content, y = page_header(
        c,
        number,
        title,
        instruction,
        kicker=f"{reference}  ·  Find 8 gifts" if reference else "Find 8 gifts",
        box=box,
    )
    left, bottom, right, top = content
    legend_h = LEGEND_H
    scene_bottom = bottom + legend_h
    scene_top = y
    scene_h = scene_top - scene_bottom
    scene_w = right - left

    c.drawImage(
        ImageReader(str(composed_path)),
        left,
        scene_bottom,
        width=scene_w,
        height=scene_h,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    names = [row["name"] for row in manifest]
    col_w = scene_w / 4
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_PUZZLE_LETTER_PT)
    c.drawString(left, bottom + legend_h - 14, "Find and circle:")
    for index, name in enumerate(names):
        col = index % 4
        row = index // 4
        x = left + 8 + col * col_w
        icon_y = bottom + 42 - row * 40
        icon_path = None
        if icon_dir is not None:
            candidate = icon_dir / f"target_{name}.png"
            if candidate.is_file():
                icon_path = candidate
        if icon_path is not None:
            c.drawImage(
                ImageReader(str(icon_path)),
                x,
                icon_y - 4,
                width=22,
                height=22,
                mask="auto",
                preserveAspectRatio=True,
                anchor="c",
            )
        elif name in ICON_DRAWERS:
            ICON_DRAWERS[name](c, x, icon_y)
        ink_text(c)
        c.setFont("Helvetica", USED_PUZZLE_LETTER_PT)
        c.drawString(x + 28, icon_y + 6, f"{index + 1}. {display_name(name)}")

    placed_w = scene_w
    placed_h = scene_h
    with Image.open(composed_path) as composed_image:
        img_w, img_h = composed_image.size
    scale = min(scene_w / img_w, scene_h / img_h)
    draw_w, draw_h = img_w * scale, img_h * scale
    ox = left + (scene_w - draw_w) / 2
    oy = scene_bottom + (scene_h - draw_h) / 2
    placed_w, placed_h = draw_w, draw_h
    if answer_key:
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1.4)
        ink_text(c)
        c.setFont("Helvetica", 9)
        for row in manifest:
            cx = ox + (row["x"] + row["width"] / 2) * scale
            cy = oy + (img_h - (row["y"] + row["height"] / 2)) * scale
            radius = max(row["width"], row["height"]) * scale * 0.62
            c.circle(cx, cy, radius, fill=0, stroke=1)
            c.drawCentredString(cx, cy + radius + 3, display_name(row["name"]))

    effective_dpi = min(img_w / (placed_w / 72.0), img_h / (placed_h / 72.0)) if placed_w and placed_h else 0
    return {
        "page": number,
        "type": "search_find",
        "mission_id": mission["id"],
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": ["search_background", *names],
        "text_in_artwork": False,
        "placeholder": marked_proof,
        "artwork_status": "placeholder_only" if marked_proof else "procedural_lineart",
        "asset_integration": (
            "Background was drawn without the eight targets. Targets are separate "
            "assets placed by the compositor. Answer key uses that manifest."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "manifest": manifest,
        "composed_path": str(composed_path),
        "raster_pixel_size": [img_w, img_h],
        "placed_points": [placed_w, placed_h],
        "effective_dpi": effective_dpi,
        "drawing_area_sqin": None,
    }


def default_asset_dir() -> Path:
    path = OUTPUT_DIR / "assets"
    path.mkdir(parents=True, exist_ok=True)
    return path
