from mission_of_words.art_bible import (
    ART_BIBLE_VERSION,
    REQUIRED_QA_DIMENSIONS,
    art_bible_errors,
    load_art_bible,
)
from mission_of_words.paths import ART_BIBLE_MD


def test_art_bible_files_validate_and_lock_the_cast():
    bible = load_art_bible()
    assert art_bible_errors(bible) == []
    assert bible["version"] == ART_BIBLE_VERSION
    assert bible["code_renders_all_page_text"] is True
    ids = {person["id"] for person in bible["cast"]}
    assert {"mira_bright", "eli_bright"} <= ids
    for name in REQUIRED_QA_DIMENSIONS:
        assert name in bible["visual_qa_dimensions"]
    text = ART_BIBLE_MD.read_text(encoding="utf-8")
    assert "Mira Bright" in text
    assert "Do **not** render titles" in text or "Do not render titles" in text.replace("**", "")
