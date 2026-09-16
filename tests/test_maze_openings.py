from llk.maze import generate_maze
from llk.maze_render import assert_physical_openings
from llk.spec import load_spec


def test_every_mission_maze_has_physical_start_and_finish_gaps():
    spec = load_spec()
    for mission in spec.missions:
        maze_page = mission.pages[2]
        maze = generate_maze(maze_page.maze_grid[0], maze_page.maze_grid[1], maze_page.maze_seed)
        report = assert_physical_openings(maze)
        assert report["start_ink"] < 0.18
        assert report["finish_ink"] < 0.18
        assert report["closed_west_ink"] > 0.20


def test_opening_edges_are_not_in_drawn_segments():
    from llk.maze import opening_edges, wall_segments

    maze = generate_maze(8, 10, 20260916)
    segs = set(wall_segments(maze))
    openings = opening_edges(maze)
    assert openings["start"] not in segs
    assert openings["finish"] not in segs
