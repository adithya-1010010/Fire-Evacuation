# Overview

## What
A terminal simulation of an agent escaping a burning building. Fire appears at scripted
times. The agent senses nearby fire, checks whether its route is still safe, and runs A*
again when it is not.

## Why
It shows the basic intelligent-agent loop with only classical AI: perceive, reason, decide,
act, then the environment changes and the loop repeats.

## Design
Each part is one small file. The core never prints and never reads input.

| File | Job |
|---|---|
| `environment.py` | the 2D grid, the real fire, scripted fire events, time (tick) |
| `astar.py` | shortest safe path (A* + Manhattan) |
| `agent.py` | perceive, rules, decide, plan, act |
| `simulation.py` | runs one cycle at a time, builds status text and metrics |
| `generator.py` | random and custom environments, difficulty settings |
| `scenarios.py` | three fixed demonstration situations |
| `main.py` | terminal menu and printing (the only terminal code) |
| `gui.py` | Pygame window (the only file that imports pygame) |

## Two views, one core
`Simulation.step()` runs exactly one cycle and returns text lines. `env.grid` is a list of
lists a view can draw. `sim.agent.path` is the route still to walk, `sim.agent.walked` is the route already walked,
`sim.last_step` has the messages of the latest step and `sim.history` one sentence per step. `sim.get_metrics()` and
`sim.status_text()` give the numbers. `main.py` prints these; `gui.py` draws them. Neither
view is imported by the core, so changing a view never touches environment, agent, A*,
rules or simulation. See `gui.md`.

## What is NOT in the project
No Tkinter, no ML or RL, no probability, no smoke or heat, no save/load, no settings.

## Limitations
- One agent, one exit, four-direction movement.
- Fire is scripted; it does not spread by itself.
- The agent senses through walls (distance only, no line of sight).
- The agent knows the map (walls and exit) but not the fire until it is near it.
