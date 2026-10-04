# Viva questions and answers

**What is the agent?**
A person in a building that must reach the exit while fire appears.

**Why is it an intelligent agent?**
It perceives the environment, reasons with rules, decides, acts, and the environment changes
as a result. It repeats this every step.

**What AI techniques are used?**
Rule-based reasoning (R1-R7), A* search with the Manhattan heuristic, a small memory of seen
fire, and replanning. Nothing else.

**Why not machine learning?**
The course project is about classical AI. The problem is small and fully described by rules.

**How is the environment stored?**
As a list of lists. `grid[row][col]` holds `#`, `.`, `A`, `E` or `F`.

**What is the difference between actual fire and known fire?**
`env.fire` is the real fire. `agent.known_fire` is what the agent has seen. The agent only
sees fire within the Manhattan sensing radius (default 4). It plans only with known fire.

**How does the agent notice that its route is unsafe?**
`path_is_safe()` checks every remaining cell of the path against `known_fire` (rule R3).

**What is replanning?**
Running A* again from the current cell, with the new known fire blocked.

**Why Manhattan distance?**
The agent moves in four directions with cost 1. Manhattan distance is the exact distance with
no walls, so it never over-estimates. That makes A* return a shortest path.

**What does the priority tuple `(f, h, counter, cell)` do?**
`f` orders the heap. `h` prefers cells closer to the goal when `f` ties. `counter` stops Python
from comparing two cell tuples when `f` and `h` tie.

**When does the simulation fail?**
No safe route exists (R6), or fire appears on the agent's cell (R7), or the time limit is hit.

**How does the fire work?**
A dictionary `{tick: [cells]}`. At each tick the environment adds the listed cells.

**What does difficulty change?**
Wall density, number of fire events, when fire starts, the gap between fires, and how often a
fire is placed on the original route. It does not change A*.

**How does the random generator work?**
It fills a grid with a border and random walls, picks agent and exit cells, checks with A*
that a route exists, adds fire events, and checks a route still exists with all fire burning.
If any check fails it starts again.

**Can a generated run still fail?**
Yes. A route exists in theory, but fire can catch the agent, or seal a dead end after the
agent has already entered it.

**What are the limits?**
One agent, one exit, scripted fire, sensing through walls, no prediction of future fire.

**How is Pygame added without changing the core?**
`gui.py` creates a `Simulation`, calls `step()` on a timer and draws `env.grid`, the route
`agent.path` and `agent.known_fire`. The core never imports `gui.py` or pygame, so the
terminal version still runs without pygame installed.

**How does the user see the route A* found?**
Terminal: the route is printed as a list of cells when A* runs, and drawn as `*` on the grid.
Pygame: a yellow line from the agent to the exit. After a replan the line changes.

**How does the user see the route the agent actually took?**
The agent stores every cell it stands on in `agent.walked`. At the end the terminal prints it as
a list and as `*` on the final map, and the Pygame window draws it as a teal line and lists it in
the route report. It differs from the first A* route when the agent had to replan.
