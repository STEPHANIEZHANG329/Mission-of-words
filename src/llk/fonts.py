from __future__ import annotations

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from llk.paths import FONTS

_REGISTERED = False

FONT_TITLE = "LLK-Title"
FONT_SANS = "LLK-Sans"
FONT_SANS_BOLD = "LLK-Sans-Bold"
FONT_SANS_SEMI = "LLK-Sans-Semi"
FONT_SERIF = "LLK-Serif"
FONT_SERIF_BOLD = "LLK-Serif-Bold"
FONT_SANS_ITALIC = "LLK-Sans-Italic"


def register_fonts() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    pdfmetrics.registerFont(TTFont(FONT_TITLE, str(FONTS / "Inter-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SANS, str(FONTS / "Inter-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SANS_BOLD, str(FONTS / "Inter-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SANS_SEMI, str(FONTS / "Inter-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SANS_ITALIC, str(FONTS / "Inter-Italic.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SERIF, str(FONTS / "LiberationSerif-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SERIF_BOLD, str(FONTS / "LiberationSerif-Bold.ttf")))
    _REGISTERED = True
