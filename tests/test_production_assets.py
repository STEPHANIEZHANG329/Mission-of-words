from copy import deepcopy

from mission_of_words.book_manifest import load_mission_records
from mission_of_words.production_assets import (
    build_production_manifest,
    load_production_manifest,
    production_manifest_errors,
    prompt_text_violations,
    role_counts,
)


EXPECTED_ROLES = {
    "title_lockup": 1,
    "welcome_spot": 1,
    "missions_map": 1,
    "parent_letter": 1,
    "coloring_hero": 8,
    "search_background": 8,
    "search_target": 64,
    "maze_scene": 8,
    "faith_frame": 8,
    "faith_choice": 32,
    "bonus_activity": 2,
    "certificate_frame": 1,
    "closing_lockup": 1,
}


def test_committed_production_manifest_matches_generator_and_counts():
    committed = load_production_manifest()
    rebuilt = build_production_manifest()
    assert production_manifest_errors(committed) == []
    assert role_counts(committed) == EXPECTED_ROLES
    assert role_counts(rebuilt) == EXPECTED_ROLES
    assert len(committed["assets"]) == 136
    assert len(committed["pages"]) == 48
    assert committed["paid_generation_authorized"] is False
    code_only = [page for page in committed["pages"] if page["layout"] == "code_only"]
    assert len(code_only) == 8
    assert all(page["type"] == "answer_key" for page in code_only)
    assert all(asset["status"] == "pending" for asset in committed["assets"])
    assert all(asset["accepted"] is False for asset in committed["assets"])


def test_prompts_do_not_contain_final_page_text():
    manifest = load_production_manifest()
    missions = load_mission_records()
    for asset in manifest["assets"]:
        assert prompt_text_violations(asset, missions=missions) == []
        assert "Do not render any letters" in asset["prompt"]
        assert asset["source_prompt_hash"]
        assert asset["width_px"] >= 512
        assert asset["height_px"] >= 512
        assert asset["dpi"] == 300


def test_search_backgrounds_exclude_their_eight_targets():
    manifest = load_production_manifest()
    backgrounds = [asset for asset in manifest["assets"] if asset["role"] == "search_background"]
    assert len(backgrounds) == 8
    for asset in backgrounds:
        assert len(asset["excluded_targets"]) == 8
        for name in asset["excluded_targets"]:
            assert name in asset["prompt"]


def test_manifest_detects_accepted_status_in_this_pass():
    record = deepcopy(load_production_manifest())
    record["assets"][0]["accepted"] = True
    record["assets"][0]["status"] = "accepted"
    errors = production_manifest_errors(record)
    assert errors
