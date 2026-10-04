import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from fire_evacuation.astar import astar, manhattan

OPEN = [list("#####"),
        list("#...#"),
        list("#...#"),
        list("#...#"),
        list("#####")]


class TestAstar(unittest.TestCase):
    def test_manhattan(self):
        self.assertEqual(manhattan((1, 1), (3, 4)), 5)

    def test_path_exists_and_is_shortest(self):
        path, _ = astar(OPEN, (1, 1), (3, 3))
        self.assertEqual(path[0], (1, 1))
        self.assertEqual(path[-1], (3, 3))
        self.assertEqual(len(path) - 1, 4)

    def test_path_moves_one_cell_at_a_time(self):
        path, _ = astar(OPEN, (1, 1), (3, 3))
        for a, b in zip(path, path[1:]):
            self.assertEqual(manhattan(a, b), 1)

    def test_walls_are_avoided(self):
        grid = [list("#######"),
                list("#..#..#"),
                list("#..#..#"),
                list("#.....#"),
                list("#######")]
        path, _ = astar(grid, (1, 1), (1, 5))
        for r, c in path:
            self.assertNotEqual(grid[r][c], "#")
        self.assertEqual(len(path) - 1, 8)   # down 2, right 4, up 2

    def test_known_fire_is_avoided(self):
        path, _ = astar(OPEN, (1, 1), (1, 3), known_fire={(1, 2)})
        self.assertNotIn((1, 2), path)
        self.assertEqual(path[-1], (1, 3))

    def test_no_path_when_walls_block(self):
        grid = [list("#####"),
                list("#.#.#"),
                list("#####")]
        path, _ = astar(grid, (1, 1), (1, 3))
        self.assertIsNone(path)

    def test_no_path_when_fire_blocks(self):
        corridor = [list("#####"), list("#...#"), list("#####")]
        path, _ = astar(corridor, (1, 1), (1, 3), known_fire={(1, 2)})
        self.assertIsNone(path)

    def test_no_path_when_exit_is_on_fire(self):
        path, _ = astar(OPEN, (1, 1), (3, 3), known_fire={(3, 3)})
        self.assertIsNone(path)

    def test_nodes_explored_is_counted(self):
        _, explored = astar(OPEN, (1, 1), (3, 3))
        self.assertGreater(explored, 0)


if __name__ == "__main__":
    unittest.main()
