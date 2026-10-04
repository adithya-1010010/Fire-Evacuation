# Decision making

## What
After REASON says what the situation is, DECIDE picks the action.

| Situation (from `reason()`) | Decision (from `decide()`) |
|---|---|
| `ROUTE_OK` | `MOVE` along the current route |
| `NO_ROUTE` | run A*; `MOVE` if a path is found, else `NO_SAFE_ROUTE` |
| `ROUTE_DANGEROUS` | run A* (replan); `MOVE` if found, else `NO_SAFE_ROUTE` |
| `AT_EXIT` | `SUCCESS` |
| `ON_FIRE` | `FAIL_ON_FIRE` |

## The simulation cycle
`Simulation.step()` in `simulation.py` runs one cycle:

1. PERCEIVE: `agent.perceive()`
2. REASON: `agent.reason()`
3. DECIDE: `agent.decide(situation)`; if the decision ends the run, stop here
4. ACT: `agent.act()` moves one cell
5. ENVIRONMENT: `env.advance()` moves time forward and fire may appear
6. End checks, in this order: reached exit (success), fire on agent (fail), time limit (fail)

## What the simulation records
Every step the simulation keeps, in `sim.last_step`, one plain sentence per stage
(perceive, reason, decide, act, environment) and one summary sentence. The summaries are
added to `sim.history`. The steps that matter (fire seen or started, plan, replan, end) are
also added to `sim.events`. The terminal and the Pygame window only show these texts; they
do not decide anything.

## Decisions
- The exit check comes before the fire check. If the agent reaches the exit on the same tick
  that fire starts, it counts as escaped.
- There is a time limit of `rows * cols * 4` ticks as a safety net. It should never trigger,
  because the agent always moves along a path and fire events are finite.

## Edge cases
- If the agent sees fire on the route ahead, it replans before moving, so it never steps
  into fire it has already seen.
- The agent can still be caught by fire that appears on its own cell. This is a real failure.
