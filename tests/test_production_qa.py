from pathlib import Path

from mission_of_words.build_production import build_production
from mission_of_words.paths import OUTPUT_DIR
from mission_of_words.production_qa import PRODUCTION_PDF_NAME, evaluate_production_readiness


def test_production_readiness_is_fail_closed_without_accepted_art():
    report = evaluate_production_readiness(human_findings=[], visual_readiness="FAIL", technical_pass=True)
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert report["required_ai_asset_count"] == 136
    assert report["accepted_ai_asset_count"] == 0
    assert len(report["missing_accepted_assets"]) == 136
    assert report["human_visual_review_pass"] is False
    assert report["paid_image_calls"] == 0


def test_build_production_writes_report_not_publishable_pdf():
    report = build_production()
    assert report["production_pass"] is False
    assert (OUTPUT_DIR / "production_readiness.json").is_file()
    assert (OUTPUT_DIR / "production_readiness.md").is_file()
    assert not (OUTPUT_DIR / PRODUCTION_PDF_NAME).is_file()
    markdown = (OUTPUT_DIR / "production_readiness.md").read_text(encoding="utf-8")
    assert "not** a publishable" in markdown.lower() or "not a publishable" in markdown.lower()
