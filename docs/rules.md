# Rules

The agent uses seven explicit rules. Each one is easy to find in the code.

| Rule | Meaning | Where |
|---|---|---|
| R1 | Known fire cells are dangerous | `Agent.is_dangerous()`; A* skips `known_fire` |
| R2 | Walls cannot be traversed | `astar()`: `if grid[r][c] == WALL: continue` |
| R3 | If the current path contains known fire, the path is invalid | `Agent.path_is_safe()` -> `reason()` returns `ROUTE_DANGEROUS` |
| R4 | If there is no valid route, run A* | `Agent.decide()` calls `plan()` for `NO_ROUTE` and `ROUTE_DANGEROUS` |
| R5 | If the agent reaches the exit, the simulation succeeds | `reason()` returns `AT_EXIT`; `Simulation.step()` checks the exit after each move |
| R6 | If no safe route exists, the simulation fails | `decide()` returns `NO_SAFE_ROUTE` when A* finds no path |
| R7 | If the agent is on a fire cell, the agent fails | `reason()` returns `ON_FIRE`; `Simulation.step()` checks after the fire advances |

## Order inside `reason()`
1. on fire (R7)
2. at exit (R5)
3. no route yet (R4)
4. route has known fire (R3)
5. otherwise the route is fine

## Decisions
Rules are plain `if` statements. There is no rule engine, because seven rules do not need one.
