from mission_of_words.fonts import FONT_BODY, FONT_TITLE_BOLD, FONT_DIR, register_fonts
from mission_of_words.paths import ROOT


def test_bundled_ofl_fonts_register():
    register_fonts()
    assert (FONT_DIR / "Nunito-Regular.ttf").is_file()
    assert (FONT_DIR / "Fredoka-SemiBold.ttf").is_file()
    assert (FONT_DIR / "OFL-Nunito.txt").is_file()
    assert (FONT_DIR / "OFL-Fredoka.txt").is_file()
    assert FONT_TITLE_BOLD.startswith("LLK-")
    assert FONT_BODY.startswith("LLK-")


def test_consumer_page_modules_do_not_set_helvetica():
    for name in ("page_front.py", "page_back.py", "page_cover.py", "page_faith.py", "page_search.py", "page_maze.py", "templates.py"):
        source = (ROOT / "src" / "mission_of_words" / name).read_text(encoding="utf-8")
        assert "Helvetica" not in source, name
