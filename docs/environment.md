# Environment

## What
`Environment` (in `environment.py`) holds the building and the real fire.

## 2D grid
The grid is a list of lists, one symbol per cell:

    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'A', '.', '.', '#'],
        ['#', '.', '#', '.', '#'],
        ['#', '.', '.', 'E', '#'],
        ['#', '#', '#', '#', '#']
    ]

Symbols are constants: `WALL '#'`, `FLOOR '.'`, `AGENT 'A'`, `EXIT 'E'`, `FIRE 'F'`, and `PATH '*'`.
`PATH` is only used when printing a route; it is never stored in the grid.
A cell is `(row, column)` and is read as `grid[row][column]`.

## Implementation
- `__init__` scans the grid once to find `agent_pos` and `exit_pos`.
- `is_wall`, `in_bounds`, `is_walkable` answer questions about a cell.
- `move_agent(cell)` puts `.` where the agent was and `A` at the new cell.
- `to_text(route=None)` joins the rows, so printing is one line of code. If a route (list of
  cells) is given, its floor cells are shown as `*`. The agent, exit and fire keep their symbols.
  The grid itself is not changed.

## Fire events
`fire_events` is a dictionary `{tick: [cells]}`, for example `{6: [(5, 8)], 12: [(6, 8)]}`.
`advance()` adds one to `tick`, looks up that tick, and puts the cells into the set
`env.fire` (the real fire) and into the grid as `F`. It returns the cells that just caught fire.
Events are fixed in advance; there is no probability and no spreading.

## Decisions
- The environment keeps the real fire (`env.fire`). The agent keeps only what it has seen.
- Fire on a wall cell is ignored.

## Edge cases
- If fire appears on the agent's cell, the grid shows `F` there and the simulation fails (R7).
- Tick 0 is the start. The first possible fire event is at tick 1.

## Testing
`tests/test_environment.py`: dimensions, agent and exit position, wall walkability,
fire events at the right tick, moving the agent, printing.
