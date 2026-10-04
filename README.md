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
