"""Preset scenarios: fixed maps and fixed fire events.

Each map is a corridor building. Row 1 is the short route, row 3 (and row 5) are longer
routes that join the exit through column 13.
"""

from .environment import Environment

TWO_LANES = [
    "###############",
    "#A...........E#",
    "#.###########.#",
    "#.............#",
    "###############",
]

THREE_LANES = [
    "###############",
    "#A...........E#",
    "#.###########.#",
    "#.............#",
    "#.###########.#",
    "#.............#",
    "###############",
]


def _build(lines, fire_events, name):
    grid = [list(line) for line in lines]
    return Environment(grid, fire_events, name)


def fire_blocks_route():
    """Fire appears on the short route once -> one replan."""
    return _build(TWO_LANES, {3: [(1, 7)]}, "Fire Blocks Route")


def multiple_replanning():
    """Fire blocks the short route, later blocks the second route -> two replans."""
    return _build(THREE_LANES, {3: [(1, 7)], 9: [(3, 7)]}, "Multiple Replanning")


def no_safe_route():
    """Fire blocks both routes -> no safe route, the simulation fails."""
    return _build(TWO_LANES, {3: [(1, 7)], 9: [(3, 7)]}, "No Safe Route")


SCENARIOS = [fire_blocks_route, multiple_replanning, no_safe_route]
