import json
from copy import deepcopy

from mission_of_words.book_manifest import (
    TARGET_PAGE_COUNT,
    answer_key_page_for,
    build_manifest,
    facing_parity,
    load_manifest,
    load_mission_records,
    manifest_consistency_errors,
    page_map,
)
from mission_of_words.paths import BOOK_MANIFEST, BOOK_RECORD, MISSION_SPEC, MISSIONS_DIR


def test_committed_manifest_has_exactly_48_contiguous_pages():
    manifest = load_manifest()
    numbers = [page["page"] for page in manifest["pages"]]
    assert numbers == list(range(1, TARGET_PAGE_COUNT + 1))
    assert manifest["target_page_count"] == 48
    assert manifest["phase"] == "B"
    assert manifest["paid_image_calls_authorized"] == 0
    assert manifest["bleed"] is False
    assert BOOK_MANIFEST.is_file()


def test_committed_manifest_matches_assembled_sources():
    assert manifest_consistency_errors() == []


def test_page_map_covers_front_missions_and_back():
    mapping = page_map()
    assert mapping[1]["type"] == "title"
    assert mapping[2]["type"] == "welcome"
    assert mapping[3]["type"] == "contents"
    assert mapping[4]["type"] == "parent_note"
    assert mapping[5]["mission_id"] == "mission_01"
    assert mapping[5]["mission_slot"] == "A"
    assert mapping[36]["mission_id"] == "mission_08"
    assert mapping[36]["mission_slot"] == "D"
    assert mapping[37]["type"] == "answer_key"
    assert mapping[44]["type"] == "answer_key"
    assert mapping[45]["type"] == "bonus_activity"
    assert mapping[46]["type"] == "bonus_activity"
    assert mapping[47]["type"] == "certificate"
    assert mapping[48]["type"] == "closing"


def test_each_mission_uses_the_required_four_slot_pattern():
    missions = load_mission_records()
    assert [mission["id"] for mission in missions] == [
        f"mission_{index:02d}" for index in range(1, 9)
    ]
    types = ("coloring", "search_find", "maze", "faith_interaction")
    slots = ("A", "B", "C", "D")
    mapping = page_map()
    for mission in missions:
        start = mission["global_page_start"]
        for offset, (slot, page_type) in enumerate(zip(slots, types)):
            page = mapping[start + offset]
            assert page["mission_slot"] == slot
            assert page["type"] == page_type
            assert page["canon_id"] == mission["canon_id"]
            assert page["artwork_status"] == "placeholder_only"


def test_facing_parity_for_all_48_pages():
    for number in range(1, 49):
        info = facing_parity(number)
        if number % 2 == 1:
            assert info == {"facing": "recto", "parity": "odd"}
        else:
            assert info == {"facing": "verso", "parity": "even"}


def test_answer_key_pages_are_one_per_mission():
    for sequence in range(1, 9):
        assert answer_key_page_for(sequence) == 36 + sequence


def test_book_record_lists_eight_missions_and_canons():
    book = json.loads(BOOK_RECORD.read_text(encoding="utf-8"))
    assert len(book["mission_ids"]) == 8
    assert len(book["canon_ids"]) == 8
    assert book["target_page_count"] == 48
    assert book["kdp_list_price_usd"] == 9.99


def test_prototype_mission_01_matches_full_book_mission_01_activity():
    prototype = json.loads(MISSION_SPEC.read_text(encoding="utf-8"))["mission"]
    full = json.loads((MISSIONS_DIR / "mission_01.json").read_text(encoding="utf-8"))
    assert prototype["title"] == full["title"]
    assert prototype["canon_id"] == full["canon_id"]
    assert prototype["scripture_reference"] == full["scripture_reference"]
    for proto_page, full_page in zip(prototype["pages"], full["pages"]):
        assert proto_page["type"] == full_page["type"]
        assert proto_page["title"] == full_page["title"]
        assert proto_page.get("child_instruction") == full_page.get("child_instruction")
        assert proto_page.get("targets") == full_page.get("targets")
        assert proto_page.get("seed") == full_page.get("seed")
        assert proto_page.get("grid") == full_page.get("grid")
        assert proto_page.get("choices") == full_page.get("choices")


def test_rebuild_detects_page_count_drift():
    rebuilt = build_manifest()
    committed = deepcopy(load_manifest())
    committed["pages"] = committed["pages"][:-1]
    errors = manifest_consistency_errors(committed=committed, rebuilt=rebuilt)
    assert errors
