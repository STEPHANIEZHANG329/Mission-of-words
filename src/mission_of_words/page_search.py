"""Page 2: Search & Find. Background and targets are independent assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from mission_of_words import procedural
from mission_of_words import art
from mission_of_words.compositor import AssetPlacement, compose_search_find
from mission_of_words.layout import DPI, USED_PUZZLE_LETTER_PT, content_box
from mission_of_words.paths import OUTPUT_DIR
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


def _scene_pixel_size(box: tuple[float, float, float, float], legend_h: float) -> tuple[int, int]:
    left, bottom, right, top = box
    width_in = (right - left) / 72.0
    height_in = (top - bottom - legend_h) / 72.0
    return max(1, round(width_in * DPI)), max(1, round(height_in * DPI))


def build_search_scene(spec: dict, dest_dir: Path) -> tuple[Path, list[dict], list[dict]]:
    page = spec["mission"]["pages"][1]
    left, bottom, right, top = content_box(2)
    legend_h = LEGEND_H
    px_w, px_h = _scene_pixel_size((left, bottom, right, top), legend_h)

    bg_path = dest_dir / "search_background.png"
    bg_record = procedural.render_search_background(bg_path, px_w, px_h)
    records = [bg_record]
    placements: list[AssetPlacement] = []
    by_name = {t["name"]: t for t in page["targets"]}
    for name in REQUIRED_TARGETS:
        target = by_name[name]
        asset_path = dest_dir / f"target_{name}.png"
        records.append(procedural.render_target(name, asset_path))
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
    return composed, manifest, records


def draw_search_find_page(
    c: canvas.Canvas,
    spec: dict,
    composed_path: Path,
    manifest: list[dict],
    *,
    answer_key: bool = False,
) -> dict:
    page = spec["mission"]["pages"][1]
    title = page["title"] if not answer_key else "Search & Find — Answer Key"
    instruction = (
        page["child_instruction"]
        if not answer_key
        else "Circles mark the same independently placed targets used on the child page."
    )
    box, y = page_header(
        c,
        2 if not answer_key else 1,
        title,
        instruction,
        kicker="Matthew 5:16  ·  Find 8 gifts from the festival",
    )
    left, bottom, right, top = box
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

    # Legend of the eight targets, 12pt names, generated from the same list.
    names = [row["name"] for row in manifest]
    col_w = scene_w / 4
    ink_text(c)
    c.setFont("Helvetica-Bold", USED_PUZZLE_LETTER_PT)
    c.drawString(left, bottom + legend_h - 14, "Find and circle:")
    for index, name in enumerate(names):
        col = index % 4
        row = index // 4
        x = left + 8 + col * col_w
        y = bottom + 42 - row * 40
        ICON_DRAWERS[name](c, x, y)
        ink_text(c)
        c.setFont("Helvetica", USED_PUZZLE_LETTER_PT)
        c.drawString(x + 28, y + 6, f"{index + 1}. {name}")

    if answer_key:
        # Overlay circles using the compositor pixel manifest, not a second list.
        with Image.open(composed_path) as composed_image:
            img_w, img_h = composed_image.size
        scale = min(scene_w / img_w, scene_h / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        ox = left + (scene_w - draw_w) / 2
        oy = scene_bottom + (scene_h - draw_h) / 2
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1.4)
        ink_text(c)
        c.setFont("Helvetica", 9)
        for row in manifest:
            cx = ox + (row["x"] + row["width"] / 2) * scale
            cy = oy + (img_h - (row["y"] + row["height"] / 2)) * scale
            radius = max(row["width"], row["height"]) * scale * 0.62
            c.circle(cx, cy, radius, fill=0, stroke=1)
            c.drawCentredString(cx, cy + radius + 3, row["name"])

    return {
        "page": 2,
        "type": "search_find",
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": ["search_background", *names],
        "text_in_artwork": False,
        "asset_integration": (
            "Background was drawn without the eight targets. Targets are separate "
            "assets placed by the compositor. Answer key uses that manifest."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "manifest": manifest,
        "composed_path": str(composed_path),
        "drawing_area_sqin": None,
    }


def default_asset_dir() -> Path:
    path = OUTPUT_DIR / "assets"
    path.mkdir(parents=True, exist_ok=True)
    return path
