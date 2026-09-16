"""Children's-publishing type stack. Helvetica is not a consumer face."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from mission_of_words.paths import ASSETS_DIR

FONT_DIR = ASSETS_DIR / "fonts"

DISPLAY = "LampkeepersDisplay"
DISPLAY_PATH = FONT_DIR / "BubblegumSans-Regular.ttf"

KICKER = "LampkeepersKicker"
KICKER_BOLD = "LampkeepersKicker-Bold"
KICKER_PATH = FONT_DIR / "Sniglet-Regular.ttf"
KICKER_BOLD_PATH = FONT_DIR / "Sniglet-ExtraBold.ttf"

BODY = "LampkeepersBody"
BODY_BOLD = "LampkeepersBody-Bold"
BODY_ITALIC = "LampkeepersBody-Italic"
BODY_BOLD_ITALIC = "LampkeepersBody-BoldItalic"
BODY_PATH = FONT_DIR / "Andika-Regular.ttf"
BODY_BOLD_PATH = FONT_DIR / "Andika-Bold.ttf"
BODY_ITALIC_PATH = FONT_DIR / "Andika-Italic.ttf"
BODY_BOLD_ITALIC_PATH = FONT_DIR / "Andika-BoldItalic.ttf"

PRAYER = "LampkeepersPrayer"
PRAYER_PATH = FONT_DIR / "PatrickHand-Regular.ttf"

FORBIDDEN_PRIMARY = ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique", "Times-Roman", "Courier")


@lru_cache(maxsize=1)
def register() -> dict[str, str]:
    missing = [
        path.name
        for path in (
            DISPLAY_PATH,
            KICKER_PATH,
            KICKER_BOLD_PATH,
            BODY_PATH,
            BODY_BOLD_PATH,
            BODY_ITALIC_PATH,
            BODY_BOLD_ITALIC_PATH,
            PRAYER_PATH,
        )
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"missing typefaces: {missing}")
    pdfmetrics.registerFont(TTFont(DISPLAY, str(DISPLAY_PATH)))
    pdfmetrics.registerFont(TTFont(KICKER, str(KICKER_PATH)))
    pdfmetrics.registerFont(TTFont(KICKER_BOLD, str(KICKER_BOLD_PATH)))
    pdfmetrics.registerFont(TTFont(BODY, str(BODY_PATH)))
    pdfmetrics.registerFont(TTFont(BODY_BOLD, str(BODY_BOLD_PATH)))
    pdfmetrics.registerFont(TTFont(BODY_ITALIC, str(BODY_ITALIC_PATH)))
    pdfmetrics.registerFont(TTFont(BODY_BOLD_ITALIC, str(BODY_BOLD_ITALIC_PATH)))
    pdfmetrics.registerFont(TTFont(PRAYER, str(PRAYER_PATH)))
    pdfmetrics.registerFontFamily(BODY, normal=BODY, bold=BODY_BOLD, italic=BODY_ITALIC, boldItalic=BODY_BOLD_ITALIC)
    pdfmetrics.registerFontFamily(KICKER, normal=KICKER, bold=KICKER_BOLD)
    return {
        "display": DISPLAY,
        "kicker": KICKER,
        "kicker_bold": KICKER_BOLD,
        "body": BODY,
        "body_bold": BODY_BOLD,
        "body_italic": BODY_ITALIC,
        "prayer": PRAYER,
    }


def primary_faces() -> tuple[str, ...]:
    register()
    return (DISPLAY, KICKER, KICKER_BOLD, BODY, BODY_BOLD, BODY_ITALIC, BODY_BOLD_ITALIC, PRAYER)
