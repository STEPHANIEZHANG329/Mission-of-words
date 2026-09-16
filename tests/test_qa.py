from copy import deepcopy
import json

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


def test_good_build_inputs_pass():
    report = evaluate_build(spec=_spec(), maze=_good_maze(), paid_image_calls=0)
    assert report["failures"] == []
    assert report["pass"] is True
    assert report["technical_pass"] is True
    assert report["production_pass"] is False
    assert report["canon_bound"] is True
    assert report["paid_image_calls"] == 0
    assert report["search_find_all_targets_present"] is True
    assert report["maze_solvable"] is True
    assert report["layout_ok"] is True


def test_missing_canon_fails():
    spec = deepcopy(_spec())
    spec["mission"].pop("canon_id")
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0)
    assert report["pass"] is False
    assert report["canon_bound"] is False
    assert any("canon" in item for item in report["failures"])


def test_missing_required_targets_fails():
    spec = deepcopy(_spec())
    spec["mission"]["pages"][1]["targets"] = spec["mission"]["pages"][1]["targets"][:7]
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0)
    assert report["pass"] is False
    assert report["search_find_all_targets_present"] is False
    assert any("search_find" in item for item in report["failures"])


def test_unsolvable_maze_fails():
    report = evaluate_build(spec=_spec(), maze=_broken_maze(), paid_image_calls=0)
    assert report["pass"] is False
    assert report["maze_solvable"] is False
    assert any("maze" in item for item in report["failures"])


def test_unsafe_layout_fails():
    spec = deepcopy(_spec())
    spec["book"]["safe_margin_inches"] = 0.25
    spec["book"]["trim_inches"] = [6.0, 9.0]
    report = evaluate_build(spec=spec, maze=_good_maze(), paid_image_calls=0)
    assert report["pass"] is False
    assert report["layout_ok"] is False
    assert any("layout" in item for item in report["failures"])


def test_paid_image_calls_fail_closed():
    report = evaluate_build(spec=_spec(), maze=_good_maze(), paid_image_calls=1)
    assert report["pass"] is False
    assert report["paid_image_calls"] == 1
    assert any("paid_image_calls" in item for item in report["failures"])
