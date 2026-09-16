from mission_of_words.build_sample import build
from mission_of_words.image_client import paid_call_count
from mission_of_words.paths import OUTPUT_DIR, ROOT


def test_build_sample_writes_passing_qa_and_pdfs():
    report = build()
    assert report["pass"] is True
    assert report["paid_image_calls"] == 0
    assert paid_call_count() == 0
    assert (OUTPUT_DIR / "BrightHearts_ShineYourLight_Phase0.pdf").is_file()
    assert (OUTPUT_DIR / "BrightHearts_ShineYourLight_AnswerKey.pdf").is_file()
    assert (OUTPUT_DIR / "qa_report.json").is_file()


def test_pr_ci_workflow_never_receives_image_secrets():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "secrets.GPT2" not in workflow
    assert "secrets." not in workflow
    assert "openai.com" not in workflow.lower()
    assert "images/generations" not in workflow
    planning = ROOT / ".github" / "workflows" / "cursor-agent-architecture-plan.yml"
    assert not planning.exists()


def test_issue_template_exists():
    template = ROOT / ".github" / "ISSUE_TEMPLATE" / "task-packet.md"
    assert template.is_file()
    text = template.read_text(encoding="utf-8")
    assert "paid_calls_allowed" in text
    assert "ops/task-packet.schema.json" in text
