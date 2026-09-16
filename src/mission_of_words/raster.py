"""Print-raster helpers. Upsampling is allowed only after source validation."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

from mission_of_words.layout import DPI


def source_native_dpi(path: Path, placed_inches: tuple[float, float]) -> float:
    with Image.open(path) as image:
        w, h = image.size
    width_in, height_in = placed_inches
    if not width_in or not height_in:
        return 0.0
    return min(w / width_in, h / height_in)


def resample_to_print_box(src: Path, dest: Path, width_in: float, height_in: float) -> dict:
    px_w = max(1, math.ceil(width_in * DPI))
    px_h = max(1, math.ceil(height_in * DPI))
    with Image.open(src) as image:
        src_w, src_h = image.size
        fitted = image.convert("RGB").resize((px_w, px_h), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fitted.save(dest, "PNG")
    return {
        "source_pixels": [src_w, src_h],
        "print_pixels": [px_w, px_h],
        "source_native_dpi_at_box": source_native_dpi(src, (width_in, height_in)),
        "print_dpi": DPI,
        "resampled": [src_w, src_h] != [px_w, px_h],
        "path": str(dest),
    }
