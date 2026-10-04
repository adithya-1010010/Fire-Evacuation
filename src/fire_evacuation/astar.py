"""A* search on the grid. Moves: up, down, left, right. Cost of a move: 1."""

import heapq

from .environment import WALL

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal, known_fire=()):
    """Find the shortest safe path from start to goal.

    Returns (path, nodes_explored).
    path is a list of cells from start to goal, or None if there is no safe path.
    """
    rows, cols = len(grid), len(grid[0])
    if goal in known_fire:
        return None, 0

    counter = 0                                   # tie-breaker for the heap
    h = manhattan(start, goal)
    open_list = [(h, h, counter, start)]          # (f, h, counter, cell)
    g_cost = {start: 0}
    parent = {start: None}
    closed = set()
    explored = 0

    while open_list:
        f, h, _, cell = heapq.heappop(open_list)
        if cell in closed:
            continue
        closed.add(cell)
        explored += 1

        if cell == goal:                          # rebuild the path backwards
            path = []
            while cell is not None:
                path.append(cell)
                cell = parent[cell]
            path.reverse()
            return path, explored

        for dr, dc in MOVES:
            nxt = (cell[0] + dr, cell[1] + dc)
            if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols):
                continue
            if grid[nxt[0]][nxt[1]] == WALL:      # R2: walls cannot be crossed
                continue
            if nxt in known_fire:                 # R1: known fire is dangerous
                continue
            new_g = g_cost[cell] + 1
            if new_g < g_cost.get(nxt, float("inf")):
                g_cost[nxt] = new_g
                parent[nxt] = cell
                counter += 1
                new_h = manhattan(nxt, goal)
                heapq.heappush(open_list, (new_g + new_h, new_h, counter, nxt))

    return None, explored
