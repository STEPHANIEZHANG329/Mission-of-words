from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from PIL import Image


@dataclass(frozen=True)
class AssetPlacement:
    name: str
    asset_path: Path
    x_ratio: float
    y_ratio: float
    width_ratio: float

    def validate(self) -> None:
        for value, label in (
            (self.x_ratio, "x_ratio"),
            (self.y_ratio, "y_ratio"),
            (self.width_ratio, "width_ratio"),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{label} must be within [0, 1]")
        if self.width_ratio <= 0:
            raise ValueError("width_ratio must be positive")


def _boxes_overlap(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
    gap: int = 4,
) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (
        ax + aw + gap <= bx
        or bx + bw + gap <= ax
        or ay + ah + gap <= by
        or by + bh + gap <= ay
    )


def compose_search_find(
    background_path: Path,
    placements: Iterable[AssetPlacement],
    output_path: Path,
    *,
    allow_overlap: bool = False,
) -> List[dict]:
    """Alpha-compose independent target assets onto a background.

    Returns an answer manifest containing the exact target pixel rectangles.
    The hidden-object logic therefore stays deterministic and auditable even
    when the background artwork comes from a generative image model.
    """
    canvas = Image.open(background_path).convert("RGBA")
    width, height = canvas.size
    manifest: List[dict] = []
    placed_boxes: list[tuple[int, int, int, int]] = []
    names: list[str] = []

    for placement in placements:
        placement.validate()
        if placement.name in names:
            raise ValueError(f"duplicate target name: {placement.name}")
        names.append(placement.name)
        asset = Image.open(placement.asset_path).convert("RGBA")
        target_width = max(1, round(width * placement.width_ratio))
        target_height = max(1, round(asset.height * target_width / asset.width))
        asset = asset.resize((target_width, target_height), Image.Resampling.LANCZOS)

        x = round((width - target_width) * placement.x_ratio)
        y = round((height - target_height) * placement.y_ratio)
        box = (x, y, target_width, target_height)
        if x < 0 or y < 0 or x + target_width > width or y + target_height > height:
            raise ValueError(f"target {placement.name} would clip the background")
        if not allow_overlap:
            for other_name, other_box in zip(names[:-1], placed_boxes):
                if _boxes_overlap(box, other_box):
                    raise ValueError(
                        f"target {placement.name} overlaps {other_name} in pixel space"
                    )
        canvas.alpha_composite(asset, (x, y))
        placed_boxes.append(box)
        manifest.append(
            {
                "name": placement.name,
                "x": x,
                "y": y,
                "width": target_width,
                "height": target_height,
                "x_ratio": placement.x_ratio,
                "y_ratio": placement.y_ratio,
                "width_ratio": placement.width_ratio,
                "cx_ratio": (x + target_width / 2) / width,
                "cy_ratio": (y + target_height / 2) / height,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, quality=95)
    return manifest
