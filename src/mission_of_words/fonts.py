"""Consumer-facing typefaces for Little Lampkeepers.

Fredoka (titles) and Nunito (body) are bundled under the SIL Open Font
License. Helvetica stays available for internal engineering overlays only.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from mission_of_words.paths import ROOT

FONT_DIR = ROOT / "assets" / "fonts"
FONT_TITLE = "LLK-Title"
FONT_TITLE_BOLD = "LLK-TitleBold"
FONT_BODY = "LLK-Body"
FONT_BODY_BOLD = "LLK-BodyBold"
FONT_ITALIC = "LLK-Italic"

_FILES = {
    FONT_TITLE: "Fredoka-SemiBold.ttf",
    FONT_TITLE_BOLD: "Fredoka-Bold.ttf",
    FONT_BODY: "Nunito-Regular.ttf",
    FONT_BODY_BOLD: "Nunito-Bold.ttf",
    FONT_ITALIC: "Nunito-Italic.ttf",
}

_registered = False


def register_fonts() -> None:
    global _registered
    if _registered:
        return
    for name, filename in _FILES.items():
        path = FONT_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"missing bundled font {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    _registered = True


register_fonts()
