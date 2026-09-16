"""Internal-only search scene density. Not publication art."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

from mission_of_words.bibles import hiding_zones_for, mission_recipe


def render_geometry_search_background(
    path: Path,
    width: int,
    height: int,
    *,
    mission: dict,
    status: str = "placeholder_only",
) -> dict:
    recipe = mission_recipe(mission["id"])
    image = Image.new("RGB", (width, height), (236, 236, 230))
    draw = ImageDraw.Draw(image)
    for x in range(-height, width + height, 28):
        draw.line([(x, 0), (x - height, height)], fill=(210, 210, 204), width=2)
    # Three depth bands so the slot is a scene, not a blank plate.
    draw.rectangle([0, 0, width, int(height * 0.32)], outline=(40, 40, 40), width=6)
    draw.rectangle([0, int(height * 0.32), width, int(height * 0.72)], outline=(40, 40, 40), width=6)
    draw.rectangle([0, int(height * 0.72), width, height], outline=(40, 40, 40), width=6)
    for zone in hiding_zones_for(mission):
        x0 = int(zone["x"] * width)
        y0 = int(zone["y"] * height)
        x1 = int((zone["x"] + zone["w"]) * width)
        y1 = int((zone["y"] + zone["h"]) * height)
        draw.ellipse([x0, y0, x1, y1], outline=(70, 70, 70), width=4)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG")
    return {
        "asset_id": f"{mission['id']}_search_background",
        "role": "search_background",
        "path": str(path),
        "status": status,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "scene_frame": recipe["search"]["scene_frame"],
        "note": "INTERNAL geometry density + hiding zones. Not publication art.",
    }
