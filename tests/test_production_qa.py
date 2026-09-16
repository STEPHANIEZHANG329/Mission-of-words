from mission_of_words.production_qa import evaluate_production
from mission_of_words.paid_images import MAX_PAID_CALLS


def test_production_qa_module_imports():
    assert callable(evaluate_production)


def test_production_pass_stays_false_without_human_review_and_visual_pass():
    report = evaluate_production(
        manifest={"pages": []},
        missions=[],
        compositions=[],
        visual={"visual_readiness": "FAIL", "pass": False, "pages": []},
        interior_pdf=__import__("pathlib").Path("/tmp/does-not-exist.pdf"),
        answer_pdf=None,
        mazes={},
        search_manifests={},
        ledger={"paid_image_calls": 18, "estimated_spend_usd": 3.6},
        preview_count=0,
        asset_records=[],
    )
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert report["paid_image_calls"] == 18
    assert report["paid_image_calls"] <= MAX_PAID_CALLS
    assert any("visual QA" in item for item in report["failures"])
