# Intelligent Fire Evacuation Agent

A small Fundamental AI project. A person (the **agent**) is inside a building and fire appears
over time. The agent must reach the exit. It uses **classical AI only**: rule-based reasoning,
A* search with the Manhattan heuristic, a simple memory of seen fire, and replanning.

No machine learning. The core and the terminal version need no packages. An optional
Pygame window draws the same simulation.

## Run

Python 3.8 or newer.

Terminal version (nothing to install):

    python run.py

Pygame window (needs `pip install pygame`):

    python run_gui.py

Run the tests:

    python -m unittest discover tests

## Menu

    1. New Simulation   -> Random Environment | Custom Environment (rows, columns, difficulty)
    2. Preset Scenarios -> Fire Blocks Route | Multiple Replanning | No Safe Route
    3. Help
    4. Exit

## The agent cycle

    PERCEIVE -> REASON -> DECIDE -> ACT -> ENVIRONMENT -> repeat

## Symbols

    # wall    . floor    A agent    E exit    F fire    * planned route (display only)

Coordinates are written `(row, column)`, starting at `(0, 0)` in the top-left corner.

## Project layout

    run.py                     starts the terminal version
    run_gui.py                 starts the Pygame version
    src/fire_evacuation/
        environment.py         2D grid, scripted fire events
        astar.py               A* search
        agent.py               perception, rules, decision, move
        simulation.py          the cycle, status text, metrics
        generator.py           random and custom environments, difficulty
        scenarios.py           three fixed preset scenarios
        main.py                terminal menu
        gui.py                 Pygame window (draws the simulation, imports pygame)
    tests/                     unittest tests
    docs/                      explanation of every part (start with overview.md)

The core (environment, agent, A*, simulation, generator, scenarios) does not print, read
input or import pygame. `main.py` (terminal) and `gui.py` (Pygame) are two separate views
on top of it. See `docs/overview.md` and `docs/gui.md`.

## Terminal output

A routine step prints one plain sentence, for example
`Step 5: moved to (1,2). Route is safe, 17 moves left.`

When something important happens (new fire is seen, the agent plans or replans, fire appears,
the run ends) the program prints the stages in words, the **route A\* found** (as a list of
cells), the grid with the route drawn as `*`, and a status block.

At the end it prints a report: the result, what happened, **the route the agent really took**
(every cell in order), the final map (`S` start, `*` cells walked) and the metrics.

The Pygame window shows the same things: a step card in plain words, a step history, and at
the end a route report with the walked route drawn on the map. See `docs/gui.md`.
