# Random and custom generation

## What
`generator.py` builds environments for the "New Simulation" menu.

| Menu | Function | User chooses | Program chooses |
|---|---|---|---|
| Random Environment | `random_environment()` | nothing | rows and columns (10-20 each), difficulty, everything else |
| Custom Environment | `generate_environment(rows, cols, difficulty)` | rows, columns (8-40), difficulty | walls, agent, exit, fire |

## Difficulty (`DIFFICULTIES` in `generator.py`)
| | Easy | Medium | Hard |
|---|---|---|---|
| wall density (inner cells) | 10% | 18% | 25% |
| fire events | 2 | 4 | 7 |
| first fire at tick | 8 | 5 | 3 |
| ticks between fires | 6 | 4 | 3 |
| chance a fire is on the original route | 30% | 60% | 90% |

These only describe the environment. A* is the same on every difficulty.

## Steps (`_try_generate`)
1. Outer border is wall; inner cells become wall with probability `wall_density`.
2. Pick a random floor cell for the agent, and a floor cell at least `(rows + cols) // 3`
   away for the exit.
3. Run A*. The route must exist and have at least 6 moves.
4. Make fire events. Each is at `first_tick + i * gap`. With probability `on_route_chance`
   the cell is chosen from the original route, ahead of where the agent will be at that tick.
   Otherwise it is a random floor cell. Never the agent or exit cell.
5. Run A* with all fire cells blocked. A route must still exist.
6. Put `A` and `E` in the grid.

If any check fails, `generate_environment` tries again (up to 1000 times, then raises `ValueError`).

## Edge cases
- Rows or columns outside 8-40 raise `ValueError`. The menu only accepts numbers in range.
- Step 5 means a safe route always exists in principle, but timing can still beat the agent.

## Testing
`tests/test_generator.py`.
