from llk.geometry import INNER_SAFETY, TRIM_H, TRIM_W, cover_size_inches, margins_for_page, spine_width_inches
from llk.maze import generate_maze
from llk.search import validate_mission_search
from llk.spec import PAGE_COUNT, load_spec, planned_assets
from llk import PAID_CALL_CAP


def test_page_map_is_exactly_48():
    spec = load_spec()
    assert len(spec.pages) == PAGE_COUNT == 48
    assert [p["page"] for p in spec.pages] == list(range(1, 49))


def test_front_missions_back_split():
    spec = load_spec()
    assert spec.pages[0]["type"] == "title"
    assert spec.pages[3]["type"] == "parent_note"
    assert spec.pages[4]["type"] == "coloring"
    assert spec.pages[35]["type"] == "faith_interaction"
    assert spec.pages[36]["type"] == "answer_key"
    assert spec.pages[47]["type"] == "closing"


def test_eight_unique_missions_and_canon():
    spec = load_spec()
    assert len(spec.missions) == 8
    assert len({m.id for m in spec.missions}) == 8
    assert len({m.canon_id for m in spec.missions}) == 8
    assert len(spec.canon) == 8
    titles = [m.title for m in spec.missions]
    assert len(set(titles)) == 8


def test_paid_asset_cap():
    assets = planned_assets()
    assert len(assets) <= PAID_CALL_CAP
    ids = [a.asset_id for a in assets]
    assert len(ids) == len(set(ids))
    assert "cover_front" in ids
    assert "title_scene" in ids


def test_prompts_forbid_text_and_rejected_styles():
    for asset in planned_assets():
        low = asset.prompt.lower()
        assert "no text" in low or "absolutely no text" in low
        assert "stick figure" not in low
        assert "wireframe" not in low
        assert "placeholder" not in low
        assert "codex" not in low


def test_search_targets_for_every_mission():
    spec = load_spec()
    for mission in spec.missions:
        validate_mission_search(mission)


def test_mazes_solvable_and_unique():
    spec = load_spec()
    seen = set()
    for mission in spec.missions:
        maze_page = mission.pages[2]
        maze = generate_maze(maze_page.maze_grid[0], maze_page.maze_grid[1], maze_page.maze_seed)
        assert maze.path[0] == maze.start
        assert maze.path[-1] == maze.end
        key = (maze.cols, maze.rows, maze.seed)
        assert key not in seen
        seen.add(key)
        # Unique path already enforced by generator.


def test_kdp_gutter_parity():
    odd = margins_for_page(5)
    even = margins_for_page(6)
    assert odd.left == INNER_SAFETY
    assert even.right == INNER_SAFETY
    assert odd.right == even.left
    assert TRIM_W == 8.5 and TRIM_H == 11.0


def test_canon_is_public_domain_and_split():
    spec = load_spec()
    for canon in spec.canon.values():
        assert canon.license == "public_domain"
        assert canon.translation == "KJV"
        assert canon.source_text
        assert canon.child_paraphrase
        assert canon.source_text not in canon.child_paraphrase


def test_cover_geometry():
    w, h = cover_size_inches(48)
    assert w > 17.0
    assert abs(h - 11.25) < 1e-6
    assert abs(spine_width_inches(48) - 48 * 0.002252) < 1e-9


def test_faith_pages_have_usable_interaction():
    spec = load_spec()
    for mission in spec.missions:
        faith = mission.pages[3]
        assert len(faith.choices) == 4
        assert faith.drawing_prompt
        assert faith.prayer
        assert len(faith.instruction) > 20


def test_answer_keys_point_at_search_and_maze():
    spec = load_spec()
    keys = [p for p in spec.pages if p["type"] == "answer_key"]
    assert len(keys) == 8
    for key in keys:
        mission = next(m for m in spec.missions if m.id == key["mission_id"])
        assert key["answers_activity_pages"] == [
            mission.global_page_start + 1,
            mission.global_page_start + 2,
        ]
