# Agent

## What
`Agent` in `agent.py` is the decision maker. One method per stage of the cycle.

## Design
| Stage | Method | Returns |
|---|---|---|
| PERCEIVE | `perceive()` | newly seen fire cells |
| REASON | `reason()` | `ON_FIRE`, `AT_EXIT`, `NO_ROUTE`, `ROUTE_DANGEROUS` or `ROUTE_OK` |
| DECIDE | `decide(situation)` | `MOVE`, `SUCCESS`, `FAIL_ON_FIRE` or `NO_SAFE_ROUTE` |
| ACT | `act()` | the new cell |

## Data the agent holds
- `pos` current cell, `exit` exit cell
- `known_fire` set of fire cells it has seen
- `path` list of cells still to walk (the current cell is not in it)
- `walked` every cell the agent has stood on, in order (starts with the start cell)
- counters: `replans`, `astar_runs`, `nodes_last`, `nodes_total`, `astar_time`,
  `initial_path_length`

## What the agent knows
It knows the walls and the exit (it is inside its own building). It does not know about fire
until `perceive()` finds it.

## Implementation notes
- `plan()` calls `astar(grid, pos, exit, known_fire)`. If a path comes back, it is stored
  without the first cell. If not, `path` is empty and `plan()` returns `False`.
- The first call to `plan()` is the initial plan. Every later call counts as a replan.
- `act()` removes the first cell of `path`, moves the agent there and adds the cell to `walked`.
  `walked` is what the end report shows as "the route the agent took".

## Testing
`tests/test_agent.py`: perception, route checks, decisions, and full runs through `Simulation`.
