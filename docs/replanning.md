# Replanning

## What
Replanning means running A* again from the agent's current cell because the old route is no
longer safe.

## When it happens
    fire appears -> agent perceives it -> fire is in known_fire
    -> path_is_safe() is False (R3) -> reason() = ROUTE_DANGEROUS
    -> decide() runs plan() (R4) -> new path, or NO_SAFE_ROUTE (R6)

A fire that is not on the current route is remembered but does not trigger a replan.

## Seeing it
Each time A* finds a route (first plan or replan) the terminal prints it, and the grid shows it
as `*`. In the example below the first route runs along row 1; after fire at (1,7) the new
route goes around through row 3.

    #...A**F*****E#          #**A...F.....E#
    #.###########.#   --->   #*###########*#
    #.............#          #*************#

## Counting
`replans` counts every A* run after the first one. A run that finds no path still counts,
so the "No Safe Route" scenario ends with 2 replans: one that found lane 2, one that failed.

## Preset scenarios (`scenarios.py`)
All use the same corridor map. Row 1 is the short route (12 moves). Rows 3 and 5 are longer
routes that join the exit through column 13. Fire cells are `(row, column)`.

| Scenario | Fire events | Expected |
|---|---|---|
| Fire Blocks Route | tick 3 at (1,7) | 1 replan, escapes |
| Multiple Replanning | tick 3 at (1,7), tick 9 at (3,7) | 2 replans, escapes through row 5 |
| No Safe Route | tick 3 at (1,7), tick 9 at (3,7), two-lane map | 2 A* runs after the first, second finds nothing, fails |

They are fixed maps, not random. The tests check the replan counts and the failure.

## Limitations
The agent only replans after it sees the fire. If it is far away it walks toward the fire
until it is within the sensing radius.

## Route found vs route taken
The route A* finds is a plan. The route the agent takes is what it actually walks
(`agent.walked`). After a replan they differ: in "Fire Blocks Route" the first plan runs along
row 1 (12 moves), but the agent walks 3 cells along row 1, turns back, and goes round through
row 3, so it takes 22 moves. The end report shows the route taken, including that turn back.
