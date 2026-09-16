from mission_of_words.maze import generate_maze


def test_maze_is_deterministic_solvable_and_perfect():
    maze_a = generate_maze(rows=13, cols=17, seed=20260916)
    maze_b = generate_maze(rows=13, cols=17, seed=20260916)

    assert maze_a.passages == maze_b.passages
    assert maze_a.is_perfect()
    path = maze_a.solve()
    assert path[0] == maze_a.start
    assert path[-1] == maze_a.finish
    assert len(path) > 2


def test_perfect_maze_has_n_minus_one_edges():
    maze = generate_maze(rows=7, cols=9, seed=42)
    assert maze.edge_count() == maze.rows * maze.cols - 1
