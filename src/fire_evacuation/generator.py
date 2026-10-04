"""Random environment generator. Keeps trying until it makes a valid environment."""

import random

from .astar import astar, manhattan
from .environment import Environment, WALL, FLOOR, AGENT, EXIT

MIN_SIZE = 8
MAX_SIZE = 40

# Difficulty only changes the environment, never the A* algorithm.
DIFFICULTIES = {
    "Easy":   {"wall_density": 0.10, "fire_count": 2, "first_tick": 8, "gap": 6, "on_route_chance": 0.3},
    "Medium": {"wall_density": 0.18, "fire_count": 4, "first_tick": 5, "gap": 4, "on_route_chance": 0.6},
    "Hard":   {"wall_density": 0.25, "fire_count": 7, "first_tick": 3, "gap": 3, "on_route_chance": 0.9},
}


def random_environment(rng=None):
    """Program chooses everything: size and difficulty."""
    rng = rng or random.Random()
    rows = rng.randint(10, 20)
    cols = rng.randint(10, 20)
    difficulty = rng.choice(list(DIFFICULTIES))
    return generate_environment(rows, cols, difficulty, rng)


def generate_environment(rows, cols, difficulty="Medium", rng=None):
    """User chooses rows, columns and difficulty. Program builds the rest."""
    if not (MIN_SIZE <= rows <= MAX_SIZE and MIN_SIZE <= cols <= MAX_SIZE):
        raise ValueError(f"rows and columns must be between {MIN_SIZE} and {MAX_SIZE}")
    rng = rng or random.Random()
    settings = DIFFICULTIES[difficulty]
    for _ in range(1000):                       # invalid? just try again
        env = _try_generate(rows, cols, settings, rng)
        if env is not None:
            env.name = f"Generated {rows}x{cols} ({difficulty})"
            return env
    raise ValueError("Could not generate a valid environment")


def _try_generate(rows, cols, settings, rng):
    # 1. outer wall + random inner walls
    grid = [[FLOOR] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            on_border = r in (0, rows - 1) or c in (0, cols - 1)
            if on_border or rng.random() < settings["wall_density"]:
                grid[r][c] = WALL

    # 2. agent and exit on floor cells, far enough apart
    floor = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == FLOOR]
    if len(floor) < 2:
        return None
    start = rng.choice(floor)
    far = [cell for cell in floor if manhattan(start, cell) >= (rows + cols) // 3]
    if not far:
        return None
    goal = rng.choice(far)

    # 3. there must be a route at the start
    path, _ = astar(grid, start, goal)
    if path is None or len(path) - 1 < 6:
        return None

    # 4. scripted fire events (never on the agent or the exit)
    fire_events = _make_fire_events(floor, path, start, goal, settings, rng)

    # 5. even with ALL fires burning, one route must still exist
    all_fire = {cell for cells in fire_events.values() for cell in cells}
    survivable, _ = astar(grid, start, goal, all_fire)
    if survivable is None:
        return None

    grid[start[0]][start[1]] = AGENT
    grid[goal[0]][goal[1]] = EXIT
    return Environment(grid, fire_events)


def _make_fire_events(floor, path, start, goal, settings, rng):
    events = {}
    used = {start, goal}
    for i in range(settings["fire_count"]):
        tick = settings["first_tick"] + i * settings["gap"]
        cell = None
        # often put the fire on the original route, ahead of the agent
        if rng.random() < settings["on_route_chance"]:
            ahead = [p for k, p in enumerate(path) if tick + 2 <= k < len(path) - 1 and p not in used]
            if ahead:
                cell = rng.choice(ahead)
        if cell is None:
            cell = rng.choice([p for p in floor if p not in used])
        used.add(cell)
        events.setdefault(tick, []).append(cell)
    return events
