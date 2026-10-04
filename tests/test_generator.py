import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import random

from fire_evacuation.astar import astar
from fire_evacuation.generator import generate_environment, random_environment, DIFFICULTIES
from fire_evacuation.simulation import Simulation


class TestGenerator(unittest.TestCase):
    def check_valid(self, env):
        self.assertIsNotNone(env.agent_pos)
        self.assertIsNotNone(env.exit_pos)
        self.assertFalse(env.is_wall(env.agent_pos))
        self.assertFalse(env.is_wall(env.exit_pos))
        path, _ = astar(env.grid, env.agent_pos, env.exit_pos)
        self.assertIsNotNone(path)
        for cells in env.fire_events.values():
            for cell in cells:
                self.assertNotEqual(cell, env.agent_pos)
                self.assertNotEqual(cell, env.exit_pos)
                self.assertFalse(env.is_wall(cell))

    def test_requested_dimensions(self):
        env = generate_environment(12, 17, "Medium", random.Random(1))
        self.assertEqual(env.rows, 12)
        self.assertEqual(env.cols, 17)
        self.assertTrue(all(len(row) == 17 for row in env.grid))

    def test_all_difficulties_are_valid(self):
        for name in DIFFICULTIES:
            for seed in range(20):
                env = generate_environment(15, 15, name, random.Random(seed))
                self.check_valid(env)

    def test_random_environment_is_valid(self):
        for seed in range(20):
            self.check_valid(random_environment(random.Random(seed)))

    def test_hard_has_more_fire_than_easy(self):
        easy = generate_environment(15, 15, "Easy", random.Random(3))
        hard = generate_environment(15, 15, "Hard", random.Random(3))
        count = lambda e: sum(len(c) for c in e.fire_events.values())
        self.assertGreater(count(hard), count(easy))

    def test_bad_size_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_environment(3, 3, "Easy")

    def test_generated_environment_can_be_simulated(self):
        env = generate_environment(15, 15, "Hard", random.Random(5))
        metrics = Simulation(env).run()
        self.assertIn(metrics["success"], (True, False))


if __name__ == "__main__":
    unittest.main()
