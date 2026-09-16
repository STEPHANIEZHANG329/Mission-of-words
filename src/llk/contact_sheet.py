"""Rasterize the interior PDF into a single contact sheet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from llk.paths import OUTPUT


def render_pages(pdf_path: Path) -> list[Image.Image]:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError("pypdfium2 is required to build the contact sheet") from exc
    doc = pdfium.PdfDocument(str(pdf_path))
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=110 / 72)
        pages.append(bitmap.to_pil().convert("RGB"))
    return pages


def build_contact_sheet(pdf_path: Path, dest: Path, cols: int = 8, rows: int = 6) -> Path:
    pages = render_pages(pdf_path)
    if len(pages) != 48:
        raise RuntimeError(f"contact sheet expected 48 pages, got {len(pages)}")
    thumb_w, thumb_h = 160, 208
    pad = 8
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + pad) + pad), (255, 255, 255))
    for i, page in enumerate(pages):
        r, col = divmod(i, cols)
        thumb = page.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (pad + col * (thumb_w + pad), pad + r * (thumb_h + pad)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest, "JPEG", quality=88, optimize=True)
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default=str(OUTPUT / "LittleLampkeepers_48Page_Interior_KDP.pdf"))
    parser.add_argument("--out", default=str(OUTPUT / "contact_sheet_all_pages.jpg"))
    args = parser.parse_args(argv)
    path = build_contact_sheet(Path(args.pdf), Path(args.out))
    print(f"WROTE {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
