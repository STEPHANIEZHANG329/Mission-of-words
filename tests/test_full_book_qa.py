from copy import deepcopy

from mission_of_words.book_manifest import build_manifest, load_manifest, load_mission_records
from mission_of_words.full_book_qa import evaluate_full_book
from mission_of_words.image_client import paid_call_count
from mission_of_words.layout import (
    INNER_SAFETY_INCHES,
    MIN_ANSWER_KEY_PT,
    MIN_INSTRUCTION_PT,
    MIN_PUZZLE_LETTER_PT,
    OUTER_SAFETY_INCHES,
    USED_ANSWER_KEY_PT,
    USED_INSTRUCTION_PT,
    USED_PUZZLE_LETTER_PT,
    page_margins_inches,
)


def test_blueprint_passes_and_production_stays_closed_without_proof():
    report = evaluate_full_book()
    assert report["failures"] == []
    assert report["blueprint_pass"] is True
    assert report["technical_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert report["paid_image_calls"] == 0
    assert report["estimated_spend_usd"] == 0
    assert report["page_count"] == 48
    assert report["canon_bound_count"] == 8
    assert report["all_canons_bound"] is True
    assert report["facing_page_parity_ok"] is True
    assert report["font_floors_ok"] is True
    assert report["answer_key_linkage_ok"] is True
    assert report["unique_content_ok"] is True
    assert report["unfilled_art_slots"] == 48
    assert report["placeholder_assets_present"] is True
    assert report["interior_pdf_present"] is False
    assert paid_call_count() == 0
    assert report["blockers"]


def test_paid_image_calls_fail_closed_for_full_book():
    report = evaluate_full_book(paid_image_calls=1)
    assert report["blueprint_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert any("paid_image_calls" in item for item in report["failures"])


def test_duplicated_search_targets_fail_uniqueness():
    missions = load_mission_records()
    missions[1]["pages"][1]["targets"] = deepcopy(missions[0]["pages"][1]["targets"])
    report = evaluate_full_book(manifest=load_manifest(), missions=missions)
    assert report["unique_content_ok"] is False
    assert report["blueprint_pass"] is False
    assert any("search-find target set" in item for item in report["failures"])


def test_overlapping_search_targets_fail():
    missions = load_mission_records()
    first = missions[1]["pages"][1]["targets"][0]
    missions[1]["pages"][1]["targets"][1]["x"] = first["x"]
    missions[1]["pages"][1]["targets"][1]["y"] = first["y"]
    missions[1]["pages"][1]["targets"][1]["scale"] = first["scale"]
    report = evaluate_full_book(manifest=load_manifest(), missions=missions)
    assert report["blueprint_pass"] is False
    assert any("unsafe overlap" in item for item in report["failures"])


def test_copied_maze_seed_fails_uniqueness():
    missions = load_mission_records()
    missions[2]["pages"][2]["seed"] = missions[0]["pages"][2]["seed"]
    report = evaluate_full_book(manifest=load_manifest(), missions=missions)
    assert report["unique_content_ok"] is False
    assert any("maze seed" in item for item in report["failures"])


def test_copied_faith_choices_fail_uniqueness():
    missions = load_mission_records()
    missions[3]["pages"][3]["choices"] = deepcopy(missions[0]["pages"][3]["choices"])
    report = evaluate_full_book(manifest=load_manifest(), missions=missions)
    assert report["unique_content_ok"] is False
    assert any("faith choice labels" in item for item in report["failures"])


def test_broken_answer_key_linkage_fails():
    manifest = deepcopy(load_manifest())
    for page in manifest["pages"]:
        if page["page"] == 37:
            page["answers_activity_pages"] = [6]
            page["answer_sources"] = page["answer_sources"][:1]
    report = evaluate_full_book(manifest=manifest, missions=load_mission_records())
    assert report["answer_key_linkage_ok"] is False
    assert report["blueprint_pass"] is False
    assert any("answer_key" in item for item in report["failures"])


def test_search_page_without_answer_key_fails():
    manifest = deepcopy(load_manifest())
    for page in manifest["pages"]:
        if page["page"] == 6:
            page["answer_key_page"] = None
    report = evaluate_full_book(manifest=manifest, missions=load_mission_records())
    assert report["answer_key_linkage_ok"] is False
    assert any("no answer_key_page" in item for item in report["failures"])


def test_font_floors_are_enforced_on_the_48_page_book():
    assert USED_INSTRUCTION_PT >= MIN_INSTRUCTION_PT >= 12
    assert USED_PUZZLE_LETTER_PT >= MIN_PUZZLE_LETTER_PT >= 12
    assert USED_ANSWER_KEY_PT >= MIN_ANSWER_KEY_PT >= 9
    manifest = load_manifest()
    assert manifest["min_instruction_pt"] >= 12
    assert manifest["min_puzzle_letter_pt"] >= 12
    assert manifest["min_answer_key_pt"] >= 9


def test_all_48_pages_have_facing_page_parity():
    for number in range(1, 49):
        margins = page_margins_inches(number)
        assert margins["inner"] == INNER_SAFETY_INCHES
        assert margins["outer"] == OUTER_SAFETY_INCHES
        assert INNER_SAFETY_INCHES > OUTER_SAFETY_INCHES
        if number % 2 == 1:
            assert margins["left"] == INNER_SAFETY_INCHES
            assert margins["right"] == OUTER_SAFETY_INCHES
        else:
            assert margins["right"] == INNER_SAFETY_INCHES
            assert margins["left"] == OUTER_SAFETY_INCHES


def test_missing_page_fails_page_count():
    manifest = deepcopy(build_manifest())
    manifest["pages"] = manifest["pages"][:-1]
    report = evaluate_full_book(manifest=manifest, missions=load_mission_records())
    assert report["blueprint_pass"] is False
    assert report["page_count"] == 47
    assert any("contiguous pages" in item for item in report["failures"])
