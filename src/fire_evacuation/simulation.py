"""Simulation: runs the cycle PERCEIVE -> REASON -> DECIDE -> ACT -> ENVIRONMENT."""

import textwrap

from .agent import (Agent, NO_SAFE_ROUTE, FAIL_ON_FIRE, SUCCESS,
                    NO_ROUTE, ROUTE_DANGEROUS, ROUTE_OK, ON_FIRE, AT_EXIT, MOVE)

EVACUATING = "EVACUATING"
ESCAPED = "ESCAPED"
FAILED = "FAILED"

# Kinds of step (used to colour the history in the Pygame view)
K_MOVE, K_FIRE, K_PLAN, K_REPLAN, K_GOOD, K_BAD = "move", "fire", "plan", "replan", "good", "bad"


def cell_text(cell):
    return f"({cell[0]},{cell[1]})"


def cells_text(cells):
    return ", ".join(cell_text(cell) for cell in cells)


def moves_text(count):
    return f"{count} move" if count == 1 else f"{count} moves"


def route_text(cells, indent="    ", width=70):
    """(1,1) -> (1,2) -> ... as wrapped text lines."""
    text = " -> ".join(cell_text(cell) for cell in cells)
    return textwrap.wrap(text, width, initial_indent=indent, subsequent_indent=indent)


class Simulation:
    def __init__(self, env, sensing_radius=4):
        self.env = env
        self.agent = Agent(env, sensing_radius)
        self.status = EVACUATING
        self.failure_reason = None
        self.steps = 0
        self.max_ticks = env.rows * env.cols * 4   # safety limit
        self.important = False   # True when the last step is worth printing in full
        self.route_lines = []    # the route A* found in the last step (empty if none)
        self.last_step = None    # dictionary with the messages of the last step
        self.history = []        # (kind, one-line summary) for every step
        self.events = []         # the same, but only for important steps

    def is_running(self):
        return self.status == EVACUATING

    def _fail(self, reason):
        self.status = FAILED
        self.failure_reason = reason

    def step(self):
        """Run one full cycle. Returns the lines to print for this step."""
        env, agent = self.env, self.agent
        number = self.steps + 1
        self.important = False
        self.route_lines = []
        old_pos = agent.pos
        runs_before = agent.astar_runs

        # PERCEIVE
        new_fire = agent.perceive()
        if new_fire:
            perceive = "Saw new fire at " + cells_text(new_fire) + "."
            self.important = True
        else:
            perceive = f"No new fire within {agent.sensing_radius} cells."

        # REASON
        situation = agent.reason()
        blocking = [cell for cell in agent.path if agent.is_dangerous(cell)]
        if situation == ROUTE_DANGEROUS:
            reason = "Known fire at " + cells_text(blocking) + " is on my route, so the route is not safe."
        elif situation == NO_ROUTE:
            reason = "I do not have a route yet."
        elif situation == ROUTE_OK:
            reason = f"My route is still safe ({moves_text(len(agent.path))} left)."
        elif situation == AT_EXIT:
            reason = "I am at the exit."
        else:
            reason = "I am standing on fire."

        # DECIDE
        decision = agent.decide(situation)
        planned = agent.astar_runs > runs_before
        first_plan = planned and runs_before == 0
        route_length = len(agent.path)           # measured now, before the agent moves
        if planned:
            self.important = True
            verb = "Plan a route" if first_plan else "Replan"
            if decision == NO_SAFE_ROUTE:                       # R6
                decide = f"{verb} with A*: no safe route exists."
            else:
                decide = f"{verb} with A*: found a route of {moves_text(route_length)}."
                self.route_lines = route_text([agent.pos] + agent.path)
        elif decision == MOVE:
            decide = "Keep following the current route."
        elif decision == SUCCESS:
            decide = "Stop: the exit is reached."
        else:
            decide = "Nothing can be done."

        # ACT and ENVIRONMENT
        act = None
        world = None
        started = []
        if decision == NO_SAFE_ROUTE:                           # R6
            self._fail("No safe route to the exit")
        elif decision == FAIL_ON_FIRE:                          # R7
            self._fail("Agent is standing on fire")
        elif decision == SUCCESS:                               # R5
            self.status = ESCAPED
        else:
            cell = agent.act()
            self.steps += 1
            act = f"Move from {cell_text(old_pos)} to {cell_text(cell)}."
            started = env.advance()
            if started:
                world = "Fire started at " + cells_text(started) + "."
                self.important = True
            if agent.pos == agent.exit:                         # R5
                self.status = ESCAPED
            elif env.agent_on_fire():                           # R7
                self._fail("Fire reached the agent at " + cell_text(agent.pos))
            elif env.tick >= self.max_ticks:
                self._fail("Time limit reached")
        if not self.is_running():
            self.important = True

        # one-line summary for the history
        parts = []
        if new_fire:
            parts.append("saw fire at " + cells_text(new_fire))
        if planned:
            if decision == NO_SAFE_ROUTE:
                parts.append("replanned with A*: no safe route exists")
            elif first_plan:
                parts.append(f"planned a route with A* ({moves_text(route_length)})")
            else:
                parts.append(f"route blocked, replanned with A* ({moves_text(route_length)})")
        if act is not None:
            parts.append("moved to " + cell_text(agent.pos))
        if started:
            parts.append("fire started at " + cells_text(started))
        if parts:
            summary = f"Step {number}: " + "; ".join(parts) + "."
        else:
            summary = f"Step {number}: moved to {cell_text(agent.pos)}. Route is safe, {moves_text(len(agent.path))} left."
        if self.status == ESCAPED:
            summary += " Reached the exit - ESCAPED."
            kind = K_GOOD
        elif self.status == FAILED:
            summary += " FAILED." if decision == NO_SAFE_ROUTE else f" FAILED: {self.failure_reason}."
            kind = K_BAD
        elif planned and not first_plan:
            kind = K_REPLAN
        elif first_plan:
            kind = K_PLAN
        elif new_fire or started:
            kind = K_FIRE
        else:
            kind = K_MOVE

        self.history.append((kind, summary))
        if self.important:
            self.events.append((kind, summary))
        self.last_step = {"number": number, "tick": env.tick, "perceive": perceive,
                          "reason": reason, "decide": decide, "act": act,
                          "environment": world, "kind": kind, "summary": summary}

        if not self.important:                                  # routine step: one line
            return [summary]
        lines = [f"--- Step {number} (tick {env.tick}) ---",
                 "Stage: PERCEIVE", "  " + perceive,
                 "Stage: REASON", "  " + reason,
                 "Stage: DECIDE", "  " + decide]
        if self.route_lines:
            lines += ["  Route:"] + self.route_lines
        if act is not None:
            lines += ["Stage: ACT", "  " + act]
        if world is not None:
            lines += ["Stage: ENVIRONMENT", "  " + world]
        return lines

    def run(self):
        """Run until the simulation ends (no printing). Returns the metrics."""
        while self.is_running():
            self.step()
        return self.get_metrics()

    def status_text(self):
        a = self.agent
        return "\n".join([f"Status: {self.status}",
                          f"Steps: {self.steps}",
                          f"Replans: {a.replans}",
                          f"Known Fire: {len(a.known_fire)}",
                          f"Current Route Length: {len(a.path)}"])

    def get_metrics(self):
        a = self.agent
        return {
            "success": self.status == ESCAPED,
            "steps": self.steps,
            "initial_path_length": a.initial_path_length,
            "replans": a.replans,
            "nodes_explored_last": a.nodes_last,
            "nodes_explored_total": a.nodes_total,
            "astar_time_ms": round(a.astar_time * 1000, 3),
            "failure_reason": self.failure_reason,
            "ticks": self.env.tick,
        }
