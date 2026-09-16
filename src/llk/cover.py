"""KDP wrap cover: back + spine + front, 0.125 in bleed, white paper spine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.pdfgen import canvas

from llk.compose import _draw_wrapped, _wrap
from llk.fonts import FONT_SANS, FONT_SANS_SEMI, FONT_TITLE, register_fonts
from llk.geometry import BLEED, TRIM_H, TRIM_W, cover_size_inches, pt, spine_width_inches
from llk.images import open_lineart, prepare_for_pdf
from llk.paths import OUTPUT, ensure_dirs
from llk.spec import load_spec

INK = Color(0.08, 0.07, 0.06)


class CoverComposer:
    def __init__(self) -> None:
        self.spec = load_spec()

    def write(self, dest: Path | None = None) -> Path:
        register_fonts()
        ensure_dirs()
        dest = dest or (OUTPUT / "LittleLampkeepers_Cover_KDP.pdf")
        width_in, height_in = cover_size_inches(48)
        spine = spine_width_inches(48)
        c = canvas.Canvas(str(dest), pagesize=(pt(width_in), pt(height_in)))
        c.setTitle(self.spec.meta["title"] + " — Cover")
        # Full cream ground.
        c.setFillColor(Color(0.98, 0.96, 0.92))
        c.rect(0, 0, pt(width_in), pt(height_in), stroke=0, fill=1)

        back_x = 0
        front_x = pt(BLEED + TRIM_W + spine)
        panel_w = pt(BLEED + TRIM_W)
        panel_h = pt(height_in)

        # Front art
        img = open_lineart("cover_front", color=True)
        tmp = OUTPUT / "_pages" / "cover_front_placed.jpg"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        prepare_for_pdf(img, max_edge=3200).save(tmp, "JPEG", quality=92)
        c.drawImage(str(tmp), front_x, 0, panel_w, panel_h, preserveAspectRatio=False, mask="auto")

        # Title band on front (code-rendered type, never baked in art)
        band_h = pt(2.15)
        c.setFillColor(Color(1, 1, 1, alpha=None))
        c.setFillColor(Color(0.99, 0.97, 0.93))
        c.rect(front_x, pt(height_in) - band_h, panel_w, band_h, stroke=0, fill=1)
        title_x = front_x + pt(BLEED + 0.45)
        title_w = pt(TRIM_W - 0.9)
        y = pt(height_in) - pt(BLEED) - 28
        c.setFillColor(INK)
        c.setFont(FONT_TITLE, 18)
        for line in _wrap(c, self.spec.meta["title"], FONT_TITLE, 18, title_w):
            c.drawString(title_x, y, line)
            y -= 22
        c.setFont(FONT_SANS, 11)
        for line in _wrap(c, self.spec.meta["subtitle"], FONT_SANS, 11, title_w):
            c.drawString(title_x, y, line)
            y -= 14
        c.setFont(FONT_SANS_SEMI, 11)
        c.drawString(title_x, y, "Ages 5–8  ·  48 pages")

        # Spine
        spine_x = pt(BLEED + TRIM_W)
        c.setFillColor(Color(0.45, 0.27, 0.12))
        c.rect(spine_x, 0, pt(spine), pt(height_in), stroke=0, fill=1)
        c.saveState()
        c.setFillColor(white)
        c.setFont(FONT_SANS_SEMI, 8)
        c.translate(spine_x + pt(spine) / 2, pt(height_in) / 2)
        c.rotate(90)
        c.drawCentredString(0, -3, self.spec.meta["cover_spine"])
        c.restoreState()

        # Back copy
        bx = pt(BLEED + 0.5)
        by = pt(height_in) - pt(BLEED) - 36
        c.setFillColor(INK)
        c.setFont(FONT_TITLE, 16)
        c.drawString(bx, by, "Little Lampkeepers")
        by -= 22
        by = _draw_wrapped(
            c,
            self.spec.meta["cover_back"],
            bx,
            by,
            FONT_SANS,
            11,
            pt(TRIM_W - 1.0),
            15,
        )
        by -= 16
        c.setFont(FONT_SANS_SEMI, 12)
        c.drawString(bx, by, "Inside this book")
        by -= 18
        for mission in self.spec.missions:
            line = f"Mission {mission.sequence}  {mission.title}  ({mission.scripture_reference})"
            by = _draw_wrapped(c, line, bx, by, FONT_SANS, 11, pt(TRIM_W - 1.0), 14) - 2
        by -= 10
        c.setFont(FONT_SANS, 9)
        _draw_wrapped(
            c,
            self.spec.meta["ownership"],
            bx,
            by,
            FONT_SANS,
            9,
            pt(TRIM_W - 1.0),
            12,
        )

        # Trim guides are not printed; KDP wants clean wrap. Do not draw crop marks.
        c.showPage()
        c.save()
        return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)
    dest = Path(args.out) if args.out else None
    path = CoverComposer().write(dest)
    print(f"WROTE {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
