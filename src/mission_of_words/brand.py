"""Consumer-facing brand lock for the finished book.

Internal ids (book_id, paths, schemas) may keep the legacy Bright Hearts
slug. Nothing a child, parent, KDP listing, cover, or interior page shows
may say Bright Hearts.
"""

from __future__ import annotations

SERIES = "Little Lampkeepers"
TITLE = "Little Lampkeepers: Shine Your Light This Fall"
SUBTITLE = "Shine Your Light This Fall"
WELCOME_HEADING = "Welcome, Little Lampkeepers"
CERTIFICATE_HEADING = "Little Lampkeepers Completion Certificate"
CLOSING_HEADING = "Keep Shining, Little Lampkeepers"
SERIES_LINE = "A Little Lampkeepers Christian Fall Activity Book"
CERTIFICATE_LINE = (
    "This certifies that ________________________ completed the Little Lampkeepers Fall missions."
)
FORBIDDEN_CONSUMER_MARK = "Bright Hearts"

INTERIOR_PDF_NAME = "LittleLampkeepers_Fall_Interior.pdf"
ANSWER_PDF_NAME = "LittleLampkeepers_Fall_AnswerKey.pdf"
COVER_PDF_NAME = "LittleLampkeepers_Fall_Cover.pdf"
