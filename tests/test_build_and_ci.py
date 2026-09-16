from mission_of_words.build_sample import INTERIOR_PDF, ANSWER_PDF, build
from mission_of_words.evaluate_full_book import evaluate as evaluate_full_book
from mission_of_words.image_client import paid_call_count
from mission_of_words.paths import OUTPUT_DIR, ROOT


def test_build_sample_writes_passing_qa_and_pdfs():
    report = build()
    assert report["pass"] is True
    assert report["technical_pass"] is True
    assert report["production_pass"] is False
    assert report["paid_image_calls"] == 0
    assert report["estimated_spend_usd"] == 0
    assert paid_call_count() == 0
    assert INTERIOR_PDF.is_file()
    assert ANSWER_PDF.is_file()
    assert (OUTPUT_DIR / "qa_report.json").is_file()
    assert (OUTPUT_DIR / "visual_qa.md").is_file()
    assert (OUTPUT_DIR / "asset_register.json").is_file()
    for index in range(1, 5):
        assert (OUTPUT_DIR / "previews" / f"page_{index:02d}.png").is_file()


def test_full_book_blueprint_writes_evidence_without_production_pass():
    report = evaluate_full_book()
    assert report["blueprint_pass"] is True
    assert report["technical_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert report["paid_image_calls"] == 0
    assert (OUTPUT_DIR / "full_book_qa.json").is_file()
    assert (OUTPUT_DIR / "book_manifest.json").is_file()
    assert (OUTPUT_DIR / "page_map.json").is_file()


def test_pr_ci_workflow_never_receives_image_secrets():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "secrets.GPT2" not in workflow
    assert "secrets." not in workflow
    assert "openai.com" not in workflow.lower()
    assert "images/generations" not in workflow
    assert "evaluate_full_book" in workflow
    assert "build_book" in workflow
    assert "production_pass" in workflow
    paid = (ROOT / ".github" / "workflows" / "phase-c-gpt2-generation.yml").read_text(encoding="utf-8")
    assert "secrets.GPT2" in paid
    assert "max_paid" not in paid.lower() or "24" in (ROOT / "ops" / "phase_c_paid_gate.json").read_text()
    planning = ROOT / ".github" / "workflows" / "cursor-agent-architecture-plan.yml"
    assert not planning.exists()
    phase0 = ROOT / ".github" / "workflows" / "phase0.yml"
    assert not phase0.exists()


def test_issue_template_exists():
    template = ROOT / ".github" / "ISSUE_TEMPLATE" / "task-packet.md"
    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    assert "paid_calls_allowed" in text
    assert "ops/task-packet.schema.json" in text
