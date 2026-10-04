import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from fire_evacuation.agent import (Agent, ROUTE_OK, ROUTE_DANGEROUS, NO_ROUTE, AT_EXIT,
                                   ON_FIRE, MOVE, SUCCESS, NO_SAFE_ROUTE)
from fire_evacuation.environment import Environment
from fire_evacuation.scenarios import fire_blocks_route, multiple_replanning, no_safe_route
from fire_evacuation.simulation import Simulation, ESCAPED, FAILED

CORRIDOR = ["#########",
            "#A.....E#",
            "#########"]


def corridor_env(fire_events=None):
    return Environment([list(row) for row in CORRIDOR], fire_events)


class TestAgentPerception(unittest.TestCase):
    def test_sees_fire_inside_radius(self):
        env = corridor_env()
        env.fire.add((1, 4))                       # distance 3
        agent = Agent(env, sensing_radius=4)
        self.assertEqual(agent.perceive(), [(1, 4)])

    def test_does_not_see_fire_outside_radius(self):
        env = corridor_env()
        env.fire.add((1, 7))                       # distance 6
        agent = Agent(env, sensing_radius=4)
        self.assertEqual(agent.perceive(), [])
        self.assertEqual(agent.known_fire, set())

    def test_known_fire_is_remembered(self):
        env = corridor_env()
        env.fire.add((1, 3))
        agent = Agent(env, sensing_radius=4)
        agent.perceive()
        agent.pos = (1, 7)                         # walk far away
        agent.perceive()
        self.assertIn((1, 3), agent.known_fire)

    def test_already_known_fire_is_not_new(self):
        env = corridor_env()
        env.fire.add((1, 3))
        agent = Agent(env, sensing_radius=4)
        agent.perceive()
        self.assertEqual(agent.perceive(), [])


class TestAgentReasoning(unittest.TestCase):
    def test_no_route_at_start(self):
        agent = Agent(corridor_env())
        self.assertEqual(agent.reason(), NO_ROUTE)

    def test_safe_route(self):
        agent = Agent(corridor_env())
        agent.plan()
        self.assertEqual(agent.reason(), ROUTE_OK)

    def test_unsafe_route_detected(self):
        env = corridor_env()
        agent = Agent(env)
        agent.plan()
        agent.known_fire.add((1, 4))               # R3
        self.assertFalse(agent.path_is_safe())
        self.assertEqual(agent.reason(), ROUTE_DANGEROUS)

    def test_at_exit(self):
        agent = Agent(corridor_env())
        agent.pos = agent.exit
        self.assertEqual(agent.reason(), AT_EXIT)
        self.assertEqual(agent.decide(AT_EXIT), SUCCESS)

    def test_on_fire(self):
        env = corridor_env()
        env.fire.add(env.agent_pos)
        self.assertEqual(Agent(env).reason(), ON_FIRE)

    def test_decide_plans_when_needed(self):
        agent = Agent(corridor_env())
        self.assertEqual(agent.decide(NO_ROUTE), MOVE)
        self.assertEqual(len(agent.path), 6)
        self.assertEqual(agent.initial_path_length, 6)

    def test_no_safe_route_decision(self):
        agent = Agent(corridor_env())
        agent.known_fire.add((1, 4))
        self.assertEqual(agent.decide(NO_ROUTE), NO_SAFE_ROUTE)


class TestSimulation(unittest.TestCase):
    def test_success_without_fire(self):
        sim = Simulation(corridor_env())
        metrics = sim.run()
        self.assertEqual(sim.status, ESCAPED)
        self.assertTrue(metrics["success"])
        self.assertEqual(metrics["steps"], 6)
        self.assertEqual(metrics["replans"], 0)

    def test_replanning_scenario(self):
        sim = Simulation(fire_blocks_route())
        metrics = sim.run()
        self.assertTrue(metrics["success"])
        self.assertEqual(metrics["replans"], 1)
        self.assertGreater(metrics["steps"], metrics["initial_path_length"])

    def test_multiple_replanning_scenario(self):
        metrics = Simulation(multiple_replanning()).run()
        self.assertTrue(metrics["success"])
        self.assertEqual(metrics["replans"], 2)

    def test_no_safe_route_scenario(self):
        sim = Simulation(no_safe_route())
        metrics = sim.run()
        self.assertEqual(sim.status, FAILED)
        self.assertFalse(metrics["success"])
        self.assertEqual(metrics["failure_reason"], "No safe route to the exit")

    def test_fire_on_agent_fails(self):
        # fire appears on the agent's own cell at tick 1 (the agent moved to (1, 2))
        sim = Simulation(corridor_env({1: [(1, 2)]}))
        sim.run()
        self.assertEqual(sim.status, FAILED)
        self.assertIn("Fire reached the agent", sim.failure_reason)

    def test_route_is_reported_when_a_plan_is_made(self):
        sim = Simulation(corridor_env())
        lines = sim.step()
        self.assertTrue(sim.route_lines)
        self.assertIn("  Route:", lines)
        self.assertIn("(1,1) -> (1,2)", sim.route_lines[0])
        self.assertIn("(1,7)", sim.route_lines[-1])       # ends at the exit

    def test_route_is_reported_again_after_a_replan(self):
        sim = Simulation(fire_blocks_route())
        routes = []
        while sim.is_running():
            sim.step()
            if sim.route_lines:
                routes.append(" ".join(sim.route_lines))
        self.assertEqual(len(routes), 2)                  # first plan + one replan
        self.assertNotEqual(routes[0], routes[1])

    def test_no_route_line_on_a_normal_step(self):
        sim = Simulation(corridor_env())
        sim.step()
        sim.step()
        self.assertEqual(sim.route_lines, [])

    def test_walked_route_is_recorded(self):
        sim = Simulation(corridor_env())
        sim.run()
        walked = sim.agent.walked
        self.assertEqual(walked[0], (1, 1))
        self.assertEqual(walked[-1], (1, 7))
        self.assertEqual(len(walked), sim.steps + 1)

    def test_walked_route_includes_the_detour_after_a_replan(self):
        sim = Simulation(fire_blocks_route())
        sim.run()
        walked = sim.agent.walked
        self.assertEqual(len(walked) - 1, sim.steps)
        self.assertIn((3, 7), walked)                     # went round through the lower lane
        self.assertNotIn((1, 7), walked)                  # never stepped on the fire

    def test_failed_run_keeps_the_route_so_far(self):
        sim = Simulation(no_safe_route())
        sim.run()
        self.assertEqual(sim.agent.walked[0], (1, 1))
        self.assertEqual(sim.agent.walked[-1], sim.agent.pos)
        self.assertGreater(len(sim.agent.walked), 1)

    def test_history_has_one_line_per_step_and_events_are_a_subset(self):
        sim = Simulation(fire_blocks_route())
        sim.run()
        self.assertEqual(len(sim.history), sim.steps)
        self.assertTrue(all(e in sim.history for e in sim.events))
        self.assertIn("replanned", " ".join(text for _, text in sim.events))
        self.assertTrue(sim.history[-1][1].endswith("ESCAPED."))

    def test_summary_reports_the_length_of_the_new_route(self):
        sim = Simulation(fire_blocks_route())
        sim.run()
        text = " ".join(text for _, text in sim.history)
        self.assertIn("planned a route with A* (12 moves)", text)
        self.assertIn("replanned with A* (19 moves)", text)

    def test_last_step_has_all_stages(self):
        sim = Simulation(corridor_env())
        sim.step()
        for key in ("perceive", "reason", "decide", "act", "environment", "summary"):
            self.assertIn(key, sim.last_step)
        self.assertIn("Move from (1,1) to (1,2)", sim.last_step["act"])

    def test_metrics_keys(self):
        metrics = Simulation(corridor_env()).run()
        for key in ("success", "steps", "initial_path_length", "replans",
                    "nodes_explored_last", "nodes_explored_total",
                    "astar_time_ms", "failure_reason", "ticks"):
            self.assertIn(key, metrics)


if __name__ == "__main__":
    unittest.main()
