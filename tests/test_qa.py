from copy import deepcopy
import hashlib
import json
from pathlib import Path

from PIL import Image

from mission_of_words.assets import REQUIRED_SEARCH_TARGET_NAMES, ensure_store
from mission_of_words.layout import page_geometry, search_find_print_space
from mission_of_words.maze import Maze, generate_maze
from mission_of_words.paths import MISSION_SPEC
from mission_of_words.qa import evaluate_build


def _spec():
    return json.loads(MISSION_SPEC.read_text(encoding="utf-8"))


def _good_maze():
    page = _spec()["mission"]["pages"][2]
    rows, cols = page["grid"]
    return generate_maze(rows=rows, cols=cols, seed=page["seed"])


def _broken_maze() -> Maze:
    cells = {(r, c): set() for r in range(2) for c in range(2)}
    return Maze(rows=2, cols=2, passages=cells, start=(0, 0), finish=(1, 1))


def _gate(status: str, evidence: str | None = "evidence/sample.md") -> dict:
    return {"status": status, "evidence_ref": evidence}


def _visual_all_pass() -> dict:
    return {
        "asset_integration": _gate("pass"),
        "child_usability": _gate("pass"),
        "prompt_to_art": _gate("pass"),
        "pages": {str(page): _gate("pass") for page in range(1, 5)},
        "owner_production_signoff": _gate("pass", "ops/owner-signoff.md"),
    }


def _seed_accepted_art(tmp_path: Path) -> Path:
    dirs = ensure_store(tmp_path)
    roles = [("coloring_bg", "coloring_background", None), ("search_bg", "search_background", None)]
    roles.extend((f"target_{name}", "search_target", name) for name in sorted(REQUIRED_SEARCH_TARGET_NAMES))
    for asset_id, role, name in roles:
        path = dirs["accepted"] / f"{asset_id}.png"
        Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(path)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        record = {
            "asset_id": asset_id,
            "role": role,
            "status": "accepted",
            "request_id": "dry-run",
            "model": None,
            "prompt": None,
            "file": str(path),
            "sha256": sha,
            "cost_usd": 0.0,
            "attempts": 0,
            "paid_call": False,
        }
        if name:
            record["name"] = name
        (dirs["provenance"] / f"{asset_id}.json").write_text(json.dumps(record), encoding="utf-8")
    return tmp_path


def test_technical_pass_with_placeholder_is_not_production_pass():
    report = evaluate_build(spec=_spec(), maze=_good_maze(), paid_image_calls=0)
    assert report["technical_pass"] is True
    assert report["technical_failures"] == []
    assert report["artwork_status"] == "placeholder_only"
    assert report["search_find_print_space"]["ok"] is True
    assert report["facing_page_safety"]["ok"] is True
    assert report["visual_qa"]["missing_evidence"] is True
    assert report["prototype_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert report["paid_image_calls"] == 0
    assert any("placeholder_only" in item for item in report["prototype_failures"])


def test_placeholder_only_fails_prototype_and_production():
    spec = deepcopy(_spec())
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0, visual_qa=_visual_all_pass())
    assert report["artwork_status"] == "placeholder_only"
    assert report["prototype_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False


def test_missing_visual_qa_fails_closed():
    report = evaluate_build(spec=_spec(), maze=_good_maze(), paid_image_calls=0, visual_qa={})
    assert report["prototype_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert any("visual QA evidence is missing" in item for item in report["prototype_failures"])


def test_any_visual_gate_fail_fails_production(tmp_path: Path):
    spec = deepcopy(_spec())
    spec["mission"]["pages"][0]["artwork_status"] = "accepted"
    visual = _visual_all_pass()
    visual["child_usability"] = _gate("fail", "reviews/usability-fail.md")
    report = evaluate_build(
        spec=spec,
        maze=_good_maze(),
        paid_image_calls=0,
        visual_qa=visual,
        assets_root=_seed_accepted_art(tmp_path),
    )
    assert report["accepted_artwork_complete"] is True
    assert report["artwork_status"] == "accepted"
    assert report["visual_qa"]["child_usability"] == "fail"
    assert report["prototype_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert any("child_usability is fail" in item for item in report["prototype_failures"])


def test_visual_pass_without_evidence_ref_fails_closed(tmp_path: Path):
    spec = deepcopy(_spec())
    spec["mission"]["pages"][0]["artwork_status"] = "accepted"
    visual = _visual_all_pass()
    visual["asset_integration"] = {"status": "pass", "evidence_ref": None}
    report = evaluate_build(
        spec=spec,
        maze=_good_maze(),
        paid_image_calls=0,
        visual_qa=visual,
        assets_root=_seed_accepted_art(tmp_path),
    )
    assert report["prototype_pass"] is False
    assert report["pass"] is False
    assert any("missing evidence_ref" in item for item in report["prototype_failures"])


def test_missing_canon_fails_technical_and_production():
    spec = deepcopy(_spec())
    spec["mission"].pop("canon_id")
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0)
    assert report["technical_pass"] is False
    assert report["pass"] is False
    assert report["canon_bound"] is False
    assert any("canon" in item for item in report["technical_failures"])


def test_missing_required_targets_fails():
    spec = deepcopy(_spec())
    spec["mission"]["pages"][1]["targets"] = spec["mission"]["pages"][1]["targets"][:7]
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0)
    assert report["technical_pass"] is False
    assert report["search_find_all_targets_present"] is False
    assert any("search_find" in item for item in report["technical_failures"])


def test_unsolvable_maze_fails():
    report = evaluate_build(spec=_spec(), maze=_broken_maze(), paid_image_calls=0)
    assert report["technical_pass"] is False
    assert report["maze_solvable"] is False
    assert any("maze" in item for item in report["technical_failures"])


def test_unsafe_layout_and_facing_page_fail():
    spec = deepcopy(_spec())
    spec["book"]["safe_margin_inches"] = 0.25
    spec["book"]["inner_margin_inches"] = 0.25
    spec["book"]["outer_margin_inches"] = 0.25
    spec["book"]["trim_inches"] = [6.0, 9.0]
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0)
    assert report["technical_pass"] is False
    assert report["layout_ok"] is False
    assert report["facing_page_safety"]["ok"] is False
    assert any("layout" in item for item in report["technical_failures"])


def test_paid_image_calls_fail_closed():
    report = evaluate_build(spec=_spec(), maze=_good_maze(), paid_image_calls=1)
    assert report["technical_pass"] is False
    assert report["pass"] is False
    assert report["paid_image_calls"] == 1
    assert any("paid_image_calls" in item for item in report["technical_failures"])


def test_facing_page_parity_swaps_inner_edge():
    recto = page_geometry(1, inner_inches=0.75, outer_inches=0.50)
    verso = page_geometry(2, inner_inches=0.75, outer_inches=0.50)
    assert recto["side"] == "recto"
    assert verso["side"] == "verso"
    assert recto["inner_edge"] == "left"
    assert verso["inner_edge"] == "right"
    assert recto["left_inches"] == 0.75
    assert verso["right_inches"] == 0.75
    assert verso["left_inches"] == 0.50


def test_search_find_print_space_uses_composed_rectangles_not_spec_boxes():
    targets = _spec()["mission"]["pages"][1]["targets"]
    result = search_find_print_space(targets)
    assert result["ok"] is True
    assert result["composed_px"]["dpi"] == 300
    assert len(result["targets"]) == 8
    lantern = next(item for item in result["targets"] if item["name"] == "lantern")
    spec_lantern = next(item for item in targets if item["name"] == "lantern")
    assert lantern["x_pt"] != spec_lantern["x"]
    assert lantern["width_px"] >= 1
    assert lantern["inside_safe_rect"] is True
