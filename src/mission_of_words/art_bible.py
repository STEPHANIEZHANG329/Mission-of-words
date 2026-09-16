"""Load and validate the Phase C Art Bible."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mission_of_words.paths import ART_BIBLE_JSON, ART_BIBLE_MD, SCHEMA_DIR
from mission_of_words.validate import validate_file, validate_instance

ART_BIBLE_VERSION = "c1.0"
PROMPT_VERSION = "c1.0"
CHARACTER_BIBLE_VERSION = "c1.0"

REQUIRED_QA_DIMENSIONS = (
    "anatomy",
    "line_consistency",
    "coloring_usability",
    "composition",
    "text_in_artwork",
    "prompt_to_art",
    "asset_integration",
    "age_suitability",
    "brand_consistency",
)

STYLE_CONTRACT = (
    "Professional US children's activity-book black-and-white line art for ages 5-8. "
    "Clean confident black outlines on white, closed colorable shapes, consistent stroke "
    "hierarchy (heavy outer / medium structure / light interior). Friendly commercial "
    "children's-book proportions. Correct anatomy: intact hands, eyes, limbs, and held "
    "objects. Large open coloring regions. Full scene with foreground, midground, and "
    "background. No muddy gray fills, photoreal shading, watercolor, sketch noise, or "
    "over-hatching. No logos, watermarks, franchise characters, or competitor layouts."
)

NO_TEXT_CONTRACT = (
    "Do not render any letters, numbers, words, titles, captions, scripture, labels, "
    "START, FINISH, page numbers, or branding. Code will add all final page text."
)

NEGATIVE_PROMPT = (
    "letters, numbers, words, titles, captions, scripture verses, page numbers, START, "
    "FINISH, watermarks, logos, Disney, anime, photoreal, grayscale shading, watercolor, "
    "sketchy construction lines, extra fingers, melted hands, broken crosses, franchise characters"
)


class ArtBibleError(ValueError):
    """Raised when the Art Bible is missing or inconsistent."""


def load_art_bible(path: Path | None = None) -> dict[str, Any]:
    bible_path = path or ART_BIBLE_JSON
    if not bible_path.is_file():
        raise ArtBibleError(f"missing art bible: {bible_path}")
    payload = json.loads(bible_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ArtBibleError("art bible must be an object")
    return payload


def art_bible_errors(bible: dict[str, Any] | None = None) -> list[str]:
    record = bible if bible is not None else load_art_bible()
    errors = validate_instance(record, SCHEMA_DIR / "art_bible.schema.json", label="art_bible")
    if record.get("version") != ART_BIBLE_VERSION:
        errors.append(f"art_bible version must be {ART_BIBLE_VERSION}")
    if record.get("prompt_version") != PROMPT_VERSION:
        errors.append(f"art_bible prompt_version must be {PROMPT_VERSION}")
    if record.get("character_bible_version") != CHARACTER_BIBLE_VERSION:
        errors.append(f"art_bible character_bible_version must be {CHARACTER_BIBLE_VERSION}")
    if record.get("code_renders_all_page_text") is not True:
        errors.append("art_bible must lock code_renders_all_page_text to true")
    dims = [str(item) for item in record.get("visual_qa_dimensions") or []]
    missing = [name for name in REQUIRED_QA_DIMENSIONS if name not in dims]
    if missing:
        errors.append(f"art_bible missing visual QA dimensions: {missing}")
    if not ART_BIBLE_MD.is_file():
        errors.append("missing content/art_bible.md")
    else:
        text = ART_BIBLE_MD.read_text(encoding="utf-8")
        for needle in ("Mira Bright", "Eli Bright", "models draw", "300 DPI", "ages 5–8"):
            if needle not in text and needle.replace("–", "-") not in text:
                errors.append(f"art_bible.md missing required contract language: {needle}")
    return errors


def validate_art_bible_files() -> list[str]:
    errors = []
    errors.extend(validate_file(ART_BIBLE_JSON, SCHEMA_DIR / "art_bible.schema.json", label="art_bible"))
    errors.extend(art_bible_errors())
    return errors


def cast_by_id(bible: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    record = bible if bible is not None else load_art_bible()
    return {str(item["id"]): item for item in record.get("cast") or []}
