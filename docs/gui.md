# Pygame view

## What
`gui.py` is a window that shows the same simulation as the terminal. It is a second view on
top of the core. Start it with `python main.py` (needs `pip install pygame`).

## Why separate
The core has no printing and no pygame. `gui.py` only does three things:
1. read key presses,
2. call `sim.step()` on a timer,
3. draw `env.grid`, `agent.path`, `agent.walked`, `agent.known_fire`, `sim.last_step`,
   `sim.history`, `sim.events` and the metrics.

If `main.py` cannot import pygame it prints a message and stops. `run.py` is unaffected.

## Screens
Same menu as the terminal, using number keys:

    Main:     1 New Simulation   2 Preset Scenarios   3 Help   4 Exit
    New:      1 Random   2 Custom   3 Back
    Custom:   UP/DOWN pick Rows / Columns / Difficulty, LEFT/RIGHT change, ENTER start, ESC back
    Presets:  1 Fire Blocks Route   2 Multiple Replanning   3 No Safe Route   4 Back

All menu screens use one centred column of buttons. The Custom screen shows what the chosen
difficulty means (wall %, number of fires, first fire tick).

## Simulation screen: the map (left)
| Colour / shape | Meaning |
|---|---|
| dark grey | wall |
| light grey | floor |
| green, letter E | exit |
| red with a yellow centre | fire that has really started |
| white ring | fire the agent knows about (`known_fire`) |
| blue circle | agent |
| teal circle, letter S | where the agent started |
| light-blue cells | the area the agent can see (Manhattan sensing radius) |
| yellow line | the route A* wants to follow next (agent -> exit) |
| teal line | the route the agent has really walked |

A red cell without a ring is a fire the agent has not seen yet. This shows the difference
between actual fire (environment) and known fire (agent). The legend under the map repeats this.

## Simulation screen: the panel (right)
1. **Status badge and five numbers**: Steps, Replans, Fire known, Route left, Clock.
2. **Step card** ("what the agent just did"): one row for each stage in plain words:
   PERCEIVE, REASON, DECIDE, ACT, and WORLD (did new fire start). The text comes from
   `sim.last_step`, the same messages the terminal prints.
3. **Step history**: the latest steps, one sentence each, newest at the bottom. Colours:
   grey = normal move, yellow = fire seen or started, blue = first plan, orange = replan,
   green = escaped, red = failed.

## When the run ends: the route report
The panel switches to a report (press `TAB` to switch back to the steps):
- **AGENT ESCAPED** or **AGENT FAILED**, with a sentence: where it started, where it ended,
  how many steps and replans (or the failure reason),
- **Route the agent took**: every cell in order, `(1,1) > (1,2) > ...`,
- **Numbers**: first route length, replans, fire seen, A* nodes explored, A* time,
- **Every step**: all steps, one sentence each (not only the important ones), coloured the same
  way as the step history.

On the map the walked route becomes a thick teal line from S to where the agent ended.
Scroll a long report with `UP`/`DOWN`, `PAGE UP`/`PAGE DOWN` or the mouse wheel / trackpad.

## Keys while running
`SPACE` pause or resume, `N` one step, `UP`/`DOWN` speed, `R` restart the same environment,
`TAB` report/steps (after the end), `ESC` menu.

## Implementation notes
- One class, `Gui`. `handle_key` decides what a key does on the current screen.
- `start(env)` keeps an untouched copy (`copy.deepcopy`) so `R` replays the same environment.
- `update_simulation()` calls `take_step()` when enough time has passed (`DELAYS` list).
- The cell size is `600 // columns` or `600 // rows`, whichever is smaller, so 8x8 to 40x40 fit.
- `wrap()` splits long messages to fit the panel; `report_lines()` builds the report.
- Text is drawn with pygame's own font by default. `USE_SYSTEM_FONT = True` at the top of `gui.py`
  switches to Helvetica / Arial / Segoe UI (drawn 2x and shrunk). Both use plain ASCII only.

## Limitations
- Fixed window size (1240 x 700), no resizing. The mouse wheel only scrolls the report.
- On a Retina (HiDPI) Mac, pygame windows are drawn at normal resolution and scaled up 2x by
  macOS, so text can look slightly soft. This comes from pygame/SDL, not from the project.
- A long walked route shows the cells in order, but a cell visited twice (after a replan that
  turns back) is drawn once on the map; the list shows both visits.
- Not tested on a real display by the author (see `testing.md`).
