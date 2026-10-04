"""The agent: perceives fire, reasons with simple rules, decides, and acts."""

import time

from .astar import astar, manhattan

# Results of reason()
ON_FIRE = "ON_FIRE"                  # R7
AT_EXIT = "AT_EXIT"                  # R5
NO_ROUTE = "NO_ROUTE"                # R4
ROUTE_DANGEROUS = "ROUTE_DANGEROUS"  # R3
ROUTE_OK = "ROUTE_OK"

# Results of decide()
MOVE = "MOVE"
SUCCESS = "SUCCESS"
FAIL_ON_FIRE = "FAIL_ON_FIRE"
NO_SAFE_ROUTE = "NO_SAFE_ROUTE"      # R6


class Agent:
    def __init__(self, env, sensing_radius=4):
        self.env = env                       # the agent knows the walls and the exit
        self.pos = env.agent_pos
        self.exit = env.exit_pos
        self.sensing_radius = sensing_radius
        self.known_fire = set()              # fire the agent has seen (its memory)
        self.path = []                       # cells still to walk (current cell not included)
        self.walked = [self.pos]             # every cell the agent has stood on, in order

        self.initial_path_length = None
        self.replans = 0
        self.astar_runs = 0
        self.nodes_last = 0
        self.nodes_total = 0
        self.astar_time = 0.0                # seconds

    # ---------- PERCEIVE ----------
    def perceive(self):
        """See real fire within the Manhattan sensing radius. Returns newly seen cells."""
        new_fire = []
        for cell in sorted(self.env.fire):
            if cell not in self.known_fire and manhattan(self.pos, cell) <= self.sensing_radius:
                self.known_fire.add(cell)
                new_fire.append(cell)
        return new_fire

    # ---------- REASON (rules) ----------
    def is_dangerous(self, cell):
        """R1: known fire cells are dangerous. (R2, walls, is handled inside A*.)"""
        return cell in self.known_fire

    def path_is_safe(self):
        """R3: if the current path contains known fire, the path is invalid."""
        for cell in self.path:
            if self.is_dangerous(cell):
                return False
        return True

    def reason(self):
        if self.pos in self.env.fire:        # R7
            return ON_FIRE
        if self.pos == self.exit:            # R5
            return AT_EXIT
        if not self.path:                    # R4: no route yet
            return NO_ROUTE
        if not self.path_is_safe():          # R3
            return ROUTE_DANGEROUS
        return ROUTE_OK

    # ---------- DECIDE ----------
    def decide(self, situation):
        if situation == ON_FIRE:
            return FAIL_ON_FIRE
        if situation == AT_EXIT:
            return SUCCESS
        if situation in (NO_ROUTE, ROUTE_DANGEROUS):
            if not self.plan():              # R4: run A*
                return NO_SAFE_ROUTE         # R6
        return MOVE

    def plan(self):
        """Run A* from the current position. Returns True if a safe route was found."""
        if self.astar_runs > 0:
            self.replans += 1
        self.astar_runs += 1

        begin = time.perf_counter()
        path, explored = astar(self.env.grid, self.pos, self.exit, self.known_fire)
        self.astar_time += time.perf_counter() - begin
        self.nodes_last = explored
        self.nodes_total += explored

        if path is None:
            self.path = []
            return False
        self.path = path[1:]
        if self.initial_path_length is None:
            self.initial_path_length = len(self.path)
        return True

    # ---------- ACT ----------
    def act(self):
        """Move one cell along the path."""
        self.pos = self.path.pop(0)
        self.walked.append(self.pos)
        self.env.move_agent(self.pos)
        return self.pos
