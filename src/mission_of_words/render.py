"""Render PDF pages to readable PNG previews."""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


def render_pdf_pages(pdf_path: Path, dest_dir: Path, *, dpi: int = 150, prefix: str = "page") -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf_path))
    paths: list[Path] = []
    scale = dpi / 72.0
    for index, page in enumerate(document):
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil().convert("RGB")
        path = dest_dir / f"{prefix}_{index + 1:02d}.png"
        image.save(path, "PNG")
        paths.append(path)
    return paths


def contact_sheet(paths: list[Path], dest: Path, *, max_width: int = 1600) -> Path:
    if len(paths) > 6:
        return contact_sheet_grid(paths, dest, columns=min(8, len(paths)), max_width=max(max_width, 2400))
    images = [Image.open(path).convert("RGB") for path in paths]
    if not images:
        raise ValueError("no preview images")
    gap = 16
    thumb_w = (max_width - gap * (len(images) - 1)) // len(images)
    thumbs = []
    for image in images:
        ratio = thumb_w / image.width
        thumbs.append(image.resize((thumb_w, max(1, round(image.height * ratio))), Image.Resampling.LANCZOS))
    height = max(img.height for img in thumbs)
    sheet = Image.new("RGB", (max_width, height), (255, 255, 255))
    x = 0
    for thumb in thumbs:
        sheet.paste(thumb, (x, (height - thumb.height) // 2))
        x += thumb.width + gap
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, "PNG")
    return dest


def contact_sheet_grid(
    paths: list[Path],
    dest: Path,
    *,
    columns: int = 8,
    max_width: int = 2400,
    gap: int = 10,
) -> Path:
    images = [Image.open(path).convert("RGB") for path in paths]
    if not images:
        raise ValueError("no preview images")
    columns = max(1, columns)
    rows = (len(images) + columns - 1) // columns
    thumb_w = (max_width - gap * (columns - 1)) // columns
    thumbs = []
    for image in images:
        ratio = thumb_w / image.width
        thumbs.append(image.resize((thumb_w, max(1, round(image.height * ratio))), Image.Resampling.LANCZOS))
    thumb_h = max(img.height for img in thumbs)
    sheet = Image.new("RGB", (max_width, rows * thumb_h + gap * (rows - 1)), (255, 255, 255))
    for index, thumb in enumerate(thumbs):
        row, col = divmod(index, columns)
        x = col * (thumb_w + gap)
        y = row * (thumb_h + gap) + (thumb_h - thumb.height) // 2
        sheet.paste(thumb, (x, y))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, "PNG")
    return dest
