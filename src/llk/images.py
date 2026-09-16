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


def knockout_white(img: Image.Image, thresh: int = 236) -> Image.Image:
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


def trim_sprite(img: Image.Image, pad: int = 4) -> Image.Image:
    """Crop transparent padding so leftover grid rules do not travel with the icon."""
    rgba = img.convert("RGBA")
    bbox = rgba.getbbox()
    if not bbox:
        return rgba
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(rgba.size[0], r + pad)
    b = min(rgba.size[1], b + pad)
    return rgba.crop((l, t, r, b))


def crop_sheet_cell(sheet: Image.Image, col: int, row: int, cols: int = 4, rows: int = 4) -> Image.Image:
    w, h = sheet.size
    cw, ch = w / cols, h / rows
    inset_x, inset_y = cw * 0.10, ch * 0.10
    box = (
        int(col * cw + inset_x),
        int(row * ch + inset_y),
        int((col + 1) * cw - inset_x),
        int((row + 1) * ch - inset_y),
    )
    return trim_sprite(knockout_white(sheet.crop(box)))


def fit_rect(iw: float, ih: float, x: float, y: float, w: float, h: float) -> tuple[float, float, float, float]:
    """Contain-fit: preserve aspect, letterbox inside the box. Never stretch."""
    if iw <= 0 or ih <= 0 or w <= 0 or h <= 0:
        return x, y, w, h
    box_aspect = w / h
    img_aspect = iw / ih
    if img_aspect > box_aspect:
        nw = w
        nh = w / img_aspect
    else:
        nh = h
        nw = h * img_aspect
    return x + (w - nw) / 2, y + (h - nh) / 2, nw, nh


def largest_white_rect(img: Image.Image, sample: int = 72, white_min: int = 246) -> tuple[float, float, float, float]:
    """Largest mostly-white axis-aligned rectangle, normalized 0-1 (x, y, w, h) from top-left."""
    gray = img.convert("L")
    ow, oh = gray.size
    full_h = max(16, int(sample * oh / ow))
    small = gray.resize((sample, full_h), Image.Resampling.BOX)
    px = small.load()
    # Certificate figures live in the lower half; only search the open upper field.
    limit = max(12, int(full_h * 0.50))
    binary = [[1 if px[x, y] >= white_min else 0 for x in range(sample)] for y in range(limit)]
    best = (0.22, 0.18, 0.56, 0.26)
    best_area = 0
    height = [0] * sample
    for y in range(limit):
        for x in range(sample):
            height[x] = height[x] + 1 if binary[y][x] else 0
        stack: list[int] = []
        x = 0
        while x <= sample:
            h = height[x] if x < sample else 0
            if not stack or h >= height[stack[-1]]:
                stack.append(x)
                x += 1
            else:
                top = stack.pop()
                width = x if not stack else x - stack[-1] - 1
                area = height[top] * width
                if area > best_area and height[top] >= 8 and width >= 12:
                    left = 0 if not stack else stack[-1] + 1
                    best_area = area
                    best = (
                        left / sample,
                        (y + 1 - height[top]) / full_h,
                        width / sample,
                        height[top] / full_h,
                    )
    return best


def prepare_for_pdf(img: Image.Image, max_edge: int = 2400) -> Image.Image:
    img = img.convert("RGB")
    w, h = img.size
    scale = max_edge / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return img
