from pathlib import Path

from mission_of_words.brand import (
    FORBIDDEN_CONSUMER_MARK,
    TITLE,
    WELCOME_HEADING,
    CERTIFICATE_HEADING,
    CLOSING_HEADING,
)
from mission_of_words.paths import BOOK_RECORD, ROOT


CONSUMER_PAGE_MODULES = (
    ROOT / "src" / "mission_of_words" / "page_front.py",
    ROOT / "src" / "mission_of_words" / "page_back.py",
    ROOT / "src" / "mission_of_words" / "page_cover.py",
)


def test_consumer_facing_title_is_little_lampkeepers():
    assert TITLE == "Little Lampkeepers: Shine Your Light This Fall"
    assert FORBIDDEN_CONSUMER_MARK not in TITLE
    assert FORBIDDEN_CONSUMER_MARK not in WELCOME_HEADING
    assert FORBIDDEN_CONSUMER_MARK not in CERTIFICATE_HEADING
    assert FORBIDDEN_CONSUMER_MARK not in CLOSING_HEADING
    book = Path(BOOK_RECORD).read_text(encoding="utf-8")
    assert TITLE in book
    assert FORBIDDEN_CONSUMER_MARK not in book


def test_page_and_cover_modules_do_not_print_legacy_series_name():
    for path in CONSUMER_PAGE_MODULES:
        source = path.read_text(encoding="utf-8")
        assert FORBIDDEN_CONSUMER_MARK not in source, path


def test_paid_workflow_is_dispatch_only_and_fault_isolated():
    paid = (ROOT / ".github" / "workflows" / "phase-c-gpt2-generation.yml").read_text(encoding="utf-8")
    header, jobs = paid.split("jobs:", 1)
    assert "workflow_dispatch:" in header
    assert "push:" not in header
    assert "RUN_PAID_GENERATION" not in paid
    assert "generate-assets:" in jobs
    assert "compose-production:" in jobs
    assert "needs: generate-assets" in jobs
    assert "Upload generated assets immediately" in jobs
    assert jobs.index("Upload generated assets immediately") < jobs.index("Build production candidate")
    assert jobs.index("generate-assets:") < jobs.index("compose-production:")
    assert "if: always()" in jobs
    compose_block = jobs.split("compose-production:")[1]
    assert "secrets.GPT2" not in compose_block
    assert "ALLOW_PAID_IMAGE_CALLS" not in compose_block
