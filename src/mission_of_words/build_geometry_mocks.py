"""Alias for the internal geometry-mock builder."""

from mission_of_words.build_book import ANSWER_PDF, INTERIOR_PDF, build

__all__ = ["ANSWER_PDF", "INTERIOR_PDF", "build"]


if __name__ == "__main__":
    from mission_of_words.build_book import build as _build

    result = _build()
    if result["paid_image_calls"] != 0 or result["production_pass"] is True or result["technical_pass"] is not True:
        raise SystemExit(1)
