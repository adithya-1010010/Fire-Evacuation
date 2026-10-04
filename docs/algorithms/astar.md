# A* search

## What
A* finds the shortest path from the agent to the exit that avoids walls and known fire.

## Why A*
The map is a grid and every move costs 1. A* with the Manhattan heuristic finds a shortest
path and usually explores far fewer cells than breadth-first search.

## Design
- Moves: up, down, left, right (`MOVES` in `astar.py`).
- `g` = moves taken so far. `h` = Manhattan distance to the goal. `f = g + h`.
- Manhattan distance never over-estimates on a 4-direction grid, so the path is shortest.
- The open list is a `heapq` of tuples `(f, h, counter, cell)`. The counter breaks ties so
  Python never compares two cells.

## Steps in the code
1. Put the start in the open list.
2. Pop the cell with the smallest `f`. Skip it if it is already closed.
3. If it is the goal, follow `parent` links backwards and reverse to get the path.
4. For each of 4 neighbours: skip if outside the grid, a wall (R2), or in `known_fire` (R1).
5. If this way to the neighbour is cheaper than any seen before, store `g`, `parent`, push it.
6. If the open list becomes empty, return `None`.

## Return value
`(path, nodes_explored)`. `path` includes the start and the goal, or is `None`.
`nodes_explored` counts cells popped and expanded.

## Edge cases
- Goal on known fire: returns `(None, 0)` straight away.
- Start equals goal: returns a one-cell path.

## Difficulty
Difficulty does not touch A*. It only changes the environment (walls and fire).

## Limitations
It plans with the fire the agent knows about now. It does not predict future fire.
