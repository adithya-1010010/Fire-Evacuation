# Metrics

`Simulation.get_metrics()` returns a plain dictionary.

| Key | Meaning |
|---|---|
| `success` | True if the agent reached the exit |
| `steps` | number of moves made |
| `initial_path_length` | moves in the first A* path (None if the first A* found nothing) |
| `replans` | A* runs after the first (see `replanning.md`) |
| `nodes_explored_last` | cells taken from the A* open list in the most recent run |
| `nodes_explored_total` | the same, added up over all runs |
| `astar_time_ms` | total time spent inside A*, in milliseconds |
| `failure_reason` | text, or None on success |
| `ticks` | the environment clock at the end |

`ticks` normally equals `steps`, because the clock advances once after every move.
Times are measured with `time.perf_counter()`; they differ from run to run.

`Simulation.status_text()` gives the live block: Status, Steps, Replans, Known Fire,
Current Route Length (moves still to go).
