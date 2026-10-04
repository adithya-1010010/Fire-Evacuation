import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from fire_evacuation.environment import Environment, WALL, FLOOR, AGENT, EXIT, FIRE

GRID = ["#####",
        "#A..#",
        "#.#.#",
        "#..E#",
        "#####"]


def make(fire_events=None):
    return Environment([list(row) for row in GRID], fire_events)


class TestEnvironment(unittest.TestCase):
    def test_dimensions(self):
        env = make()
        self.assertEqual((env.rows, env.cols), (5, 5))

    def test_grid_is_list_of_lists(self):
        env = make()
        self.assertIsInstance(env.grid, list)
        self.assertIsInstance(env.grid[0], list)

    def test_agent_and_exit_found(self):
        env = make()
        self.assertEqual(env.agent_pos, (1, 1))
        self.assertEqual(env.exit_pos, (3, 3))

    def test_wall_is_not_walkable(self):
        env = make()
        self.assertTrue(env.is_wall((2, 2)))
        self.assertFalse(env.is_walkable((2, 2)))
        self.assertTrue(env.is_walkable((1, 2)))
        self.assertFalse(env.is_walkable((-1, 0)))

    def test_fire_event_appears_at_its_tick(self):
        env = make({2: [(1, 2)]})
        self.assertEqual(env.advance(), [])            # tick 1
        self.assertEqual(env.advance(), [(1, 2)])      # tick 2
        self.assertIn((1, 2), env.fire)
        self.assertEqual(env.grid[1][2], FIRE)

    def test_fire_does_not_appear_early(self):
        env = make({5: [(1, 2)]})
        env.advance()
        self.assertEqual(env.fire, set())

    def test_move_agent_updates_grid(self):
        env = make()
        env.move_agent((1, 2))
        self.assertEqual(env.grid[1][1], FLOOR)
        self.assertEqual(env.grid[1][2], AGENT)
        self.assertEqual(env.agent_pos, (1, 2))

    def test_agent_on_fire(self):
        env = make({1: [(1, 1)]})
        env.advance()
        self.assertTrue(env.agent_on_fire())

    def test_to_text(self):
        self.assertEqual(make().to_text(), "\n".join(GRID))

    def test_to_text_marks_route_on_floor_only(self):
        text = make().to_text([(1, 1), (1, 2), (1, 3), (2, 3), (3, 3)])
        self.assertEqual(text.split("\n")[1], "#A**#")     # agent cell stays A
        self.assertEqual(text.split("\n")[3], "#..E#")     # exit cell stays E
        self.assertEqual(text.split("\n")[2], "#.#*#")

    def test_to_text_route_does_not_change_the_grid(self):
        env = make()
        env.to_text([(1, 2)])
        self.assertEqual(env.grid[1][2], FLOOR)


if __name__ == "__main__":
    unittest.main()
