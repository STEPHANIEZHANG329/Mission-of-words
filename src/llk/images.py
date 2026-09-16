from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

from llk.paths import ASSETS_ACCEPTED, ASSETS_GENERATED


def find_art(asset_id: str) -> Path:
    for folder in (ASSETS_GENERATED, ASSETS_ACCEPTED):
        for ext in (".png", ".jpg", ".jpeg"):
            path = folder / f"{asset_id}{ext}"
            if path.exists() and path.stat().st_size > 800:
                return path
    raise FileNotFoundError(f"missing accepted artwork for {asset_id}")


def open_lineart(asset_id: str, *, color: bool = False) -> Image.Image:
    img = Image.open(find_art(asset_id))
    if color:
        return img.convert("RGB")
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    return gray.convert("RGB")


def knockout_white(img: Image.Image, thresh: int = 242) -> Image.Image:
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r >= thresh and g >= thresh and b >= thresh:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                lum = int(0.3 * r + 0.59 * g + 0.11 * b)
                pixels[x, y] = (lum, lum, lum, 255)
    return rgba


def crop_sheet_cell(sheet: Image.Image, col: int, row: int, cols: int = 4, rows: int = 4) -> Image.Image:
    w, h = sheet.size
    cw, ch = w / cols, h / rows
    inset_x, inset_y = cw * 0.07, ch * 0.07
    box = (
        int(col * cw + inset_x),
        int(row * ch + inset_y),
        int((col + 1) * cw - inset_x),
        int((row + 1) * ch - inset_y),
    )
    return knockout_white(sheet.crop(box))


def prepare_for_pdf(img: Image.Image, max_edge: int = 2400) -> Image.Image:
    img = img.convert("RGB")
    w, h = img.size
    scale = max_edge / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return img
