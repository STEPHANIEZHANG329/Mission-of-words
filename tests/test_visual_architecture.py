import json
from pathlib import Path

from mission_of_words.bibles import uniqueness_report, validate_bibles
from mission_of_words.book_manifest import load_mission_records
from mission_of_words.paid_images import generation_authorized
from mission_of_words.paths import CONTENT_DIR, OPS_DIR, ROOT
from mission_of_words.proof import FORBIDDEN_PRODUCT_LABELS, INTERNAL_MOCK_MARK
from mission_of_words.typefaces import FORBIDDEN_PRIMARY


def test_bibles_are_unique_and_source_locked():
    failures = validate_bibles()
    assert failures == [], failures
    report = uniqueness_report()
    assert report["unique"] is True
    assert report["any_maze_white_window"] is False
    assert all(0.70 <= value <= 0.80 for value in report["hero_art_fractions"])
    assert all(value <= 0.14 for value in report["search_legend_fractions"])


def test_cast_and_composition_bibles_exist():
    cast = json.loads((CONTENT_DIR / "cast_style_bible.json").read_text())
    composition = json.loads((CONTENT_DIR / "composition_bible.json").read_text())
    assert [member["id"] for member in cast["cast"]] == ["mira", "eli", "joy", "caleb", "pip"]
    assert composition["owner_facing"] is False
    assert "no_text" in json.dumps(cast).lower() or "NO titles" in json.dumps(cast)
    for mission in load_mission_records():
        recipe = composition["missions"][mission["id"]]
        assert recipe["maze"]["white_window"] is False
        assert recipe["hero"]["banner"]
        assert recipe["faith"]["card_layout"]


def test_geometry_mocks_are_not_labeled_product():
    assert "NOT_PRODUCT" in "INTERNAL_LittleLampkeepers_48_GeometryMocks_NOT_PRODUCT.pdf"
    assert INTERNAL_MOCK_MARK == "INTERNAL GEOMETRY MOCK"
    for label in FORBIDDEN_PRODUCT_LABELS:
        assert "Helvetica" not in label
    assert "Helvetica" in FORBIDDEN_PRIMARY


def test_paid_generation_stays_closed(monkeypatch):
    monkeypatch.setenv("ALLOW_PAID_IMAGE_CALLS", "1")
    monkeypatch.setenv("GPT2", "must-not-be-used")
    ok, reason = generation_authorized()
    assert ok is False
    review = json.loads((OPS_DIR / "architecture_review.json").read_text())
    assert review["approved_for_paid_generation"] is False
    assert review["gpt2_spend_authorized"] is False
    gate = json.loads((OPS_DIR / "phase_c_paid_gate.json").read_text())
    assert gate["allow_paid_image_calls"] is False
    assert gate["remaining_calls"] == 0
    assert gate["owner_stop"] is True


def test_rejected_commercial_proofs_cannot_run():
    import pytest

    from mission_of_words import commercial_layout_proof, commercial_layout_proof_v2

    with pytest.raises(SystemExit, match="REJECTED"):
        commercial_layout_proof.build()
    with pytest.raises(SystemExit, match="REJECTED"):
        commercial_layout_proof_v2.build()


def test_ci_does_not_upload_commercial_product_pdfs():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "little-lampkeepers-commercial-layout-proof" not in workflow
    assert "INTERNAL_" in workflow
    assert "NOT_PRODUCT" in workflow
    assert "production_pass" in workflow
    paid = (ROOT / ".github" / "workflows" / "phase-c-gpt2-generation.yml").read_text(encoding="utf-8")
    assert "architecture_review.json" in paid
    assert "approved_for_paid_generation" in paid
