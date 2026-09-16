from copy import deepcopy

from mission_of_words.book_manifest import load_mission_records
from mission_of_words.search_difficulty import (
    MAX_WIDTH_RATIO,
    MIN_WIDTH_RATIO,
    evaluate_composed_targets,
    evaluate_search_difficulty,
)


def test_live_missions_pass_search_difficulty_rules():
    for mission in load_mission_records():
        targets = mission["pages"][1]["targets"]
        names = [target["name"] for target in targets]
        assert evaluate_search_difficulty(
            targets,
            excluded_background_objects=names,
            owner=mission["id"],
        ) == []


def test_tiny_target_fails_min_size():
    missions = load_mission_records()
    targets = deepcopy(missions[0]["pages"][1]["targets"])
    targets[0]["scale"] = MIN_WIDTH_RATIO - 0.02
    failures = evaluate_search_difficulty(targets, owner="tiny")
    assert any("below min" in item for item in failures)


def test_giant_target_fails_max_size():
    missions = load_mission_records()
    targets = deepcopy(missions[0]["pages"][1]["targets"])
    targets[0]["scale"] = MAX_WIDTH_RATIO + 0.2
    failures = evaluate_search_difficulty(targets, owner="giant")
    assert any("exceeds max" in item for item in failures)


def test_edge_and_overlap_and_ambiguity_fail():
    targets = [
        {"name": "a", "x": 0.0, "y": 0.0, "scale": 0.10},
        {"name": "b", "x": 0.0, "y": 0.0, "scale": 0.10},
        {"name": "c", "x": 0.5, "y": 0.5, "scale": 0.09},
        {"name": "d", "x": 0.6, "y": 0.5, "scale": 0.09},
        {"name": "e", "x": 0.7, "y": 0.5, "scale": 0.09},
        {"name": "f", "x": 0.8, "y": 0.5, "scale": 0.09},
        {"name": "g", "x": 0.4, "y": 0.7, "scale": 0.09},
        {"name": "a", "x": 0.3, "y": 0.3, "scale": 0.09},
    ]
    failures = evaluate_search_difficulty(targets, owner="bad")
    assert failures
    overlapped = [
        {"name": f"t{i}", "x": 0.2, "y": 0.2 + i * 0.02, "scale": 0.12}
        for i in range(8)
    ]
    overlapped[1]["x"] = overlapped[0]["x"]
    overlapped[1]["y"] = overlapped[0]["y"]
    overlapped[1]["scale"] = overlapped[0]["scale"]
    failures = evaluate_search_difficulty(overlapped, owner="overlap")
    assert any("overlap" in item for item in failures)


def test_composed_manifest_edge_and_size_checks():
    ok = [
        {"name": f"t{i}", "x": 40 + i * 80, "y": 40, "width": 70, "height": 70}
        for i in range(8)
    ]
    assert evaluate_composed_targets(ok, scene_width_px=800, scene_height_px=800) == []
    tiny = deepcopy(ok)
    tiny[0]["width"] = 10
    tiny[0]["height"] = 10
    assert any("below min" in item for item in evaluate_composed_targets(tiny, scene_width_px=800, scene_height_px=800))
    edge = deepcopy(ok)
    edge[0]["x"] = 0
    assert any("edge safety" in item for item in evaluate_composed_targets(edge, scene_width_px=800, scene_height_px=800))
    dup = deepcopy(ok)
    dup[1]["name"] = dup[0]["name"]
    assert any("unique" in item for item in evaluate_composed_targets(dup, scene_width_px=800, scene_height_px=800))
