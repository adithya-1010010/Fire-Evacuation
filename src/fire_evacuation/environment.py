"""Environment: a 2D grid (list of lists) plus scripted fire events.

Cells are (row, column) tuples. The top-left cell is (0, 0).
"""

WALL = "#"
FLOOR = "."
AGENT = "A"
EXIT = "E"
FIRE = "F"
PATH = "*"      # only used when printing: marks the route the agent plans to walk


class Environment:
    def __init__(self, grid, fire_events=None, name="Custom"):
        self.grid = grid                      # list of lists of symbols
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.fire_events = fire_events or {}  # {tick: [(row, col), ...]}
        self.name = name
        self.tick = 0
        self.fire = set()                     # cells that are REALLY burning
        self.agent_pos = None
        self.exit_pos = None
        for r in range(self.rows):
            for c in range(self.cols):
                if grid[r][c] == AGENT:
                    self.agent_pos = (r, c)
                elif grid[r][c] == EXIT:
                    self.exit_pos = (r, c)

    def in_bounds(self, cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_wall(self, cell):
        r, c = cell
        return self.grid[r][c] == WALL

    def is_walkable(self, cell):
        return self.in_bounds(cell) and not self.is_wall(cell)

    def move_agent(self, cell):
        """Move the agent symbol to a new cell."""
        r, c = self.agent_pos
        self.grid[r][c] = FLOOR
        self.agent_pos = cell
        self.grid[cell[0]][cell[1]] = AGENT

    def advance(self):
        """Move time forward one tick. Returns the cells that just caught fire."""
        self.tick += 1
        new_fire = []
        for cell in self.fire_events.get(self.tick, []):
            if self.is_walkable(cell) and cell not in self.fire:
                self.fire.add(cell)
                self.grid[cell[0]][cell[1]] = FIRE
                new_fire.append(cell)
        return new_fire

    def agent_on_fire(self):
        return self.agent_pos in self.fire

    def to_text(self, route=None):
        """The grid as text. If a route is given, its floor cells are drawn as '*'."""
        rows = [list(row) for row in self.grid]
        for r, c in route or []:
            if rows[r][c] == FLOOR:
                rows[r][c] = PATH
        return "\n".join("".join(row) for row in rows)
