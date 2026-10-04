# Testing

Run from the project root:

    python -m unittest discover tests

Uses Python's `unittest` only. 52 tests, under a second.

| File | What it checks |
|---|---|
| `test_astar.py` | path exists, shortest length, one-cell moves, walls avoided, known fire avoided, no path (walls / fire / exit on fire), nodes counted |
| `test_environment.py` | dimensions, list of lists, agent and exit found, wall walkability, fire at the right tick, not early, moving the agent, fire on agent, printing, route drawn as `*` without changing the grid |
| `test_agent.py` | perception (radius, memory), unsafe route detection, decisions, success, replanning (1 and 2), no-safe-route failure, fire on agent, route printed after a plan and again after a replan, walked route (with detour, never on fire, kept after a failure), history and events, correct route length in the summary, last-step stages, metric keys |
| `test_generator.py` | requested size, valid agent / exit, route exists, fire not on agent / exit / wall, all difficulties, Hard has more fire than Easy, bad size rejected |

## Manual checks done before packaging
- Menu paths: Random, Custom (several sizes and all three difficulties), each preset, Help, Exit.
- 40 random seeds for each difficulty at sizes 8x8 up to 40x40: every environment was valid
  and every run ended (success or failure), with no crash.
- No `tkinter` anywhere. `pygame` is imported only in `gui.py`.

## GUI testing
Pygame was not installable in the environment where this project was built, so `gui.py` has
no unit tests. Its logic (menus, custom settings, start, step, pause, restart, drawing calls
for every preset, random and 8x8 / 40x40 custom environments, report scrolling, TAB) was run
through a stand-in for pygame that draws into an image, and the frames were looked at to check the
layout and the text fit. The stand-in is not real pygame (fonts differ slightly), so check the
window on your machine. See `gui.md`.

## Edge cases not covered
Invalid menu text is handled by `ask_int` (asks again) but is not unit tested.
