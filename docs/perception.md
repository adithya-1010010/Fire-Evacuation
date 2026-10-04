# Perception

## What
The agent does not see all fire. It only notices fire inside a Manhattan sensing radius.

## Design
    Environment  -> env.fire         (actual fire)
    Agent        -> agent.known_fire (fire it has seen)

`known_fire` is a plain Python `set`.

## Implementation
`Agent.perceive()` in `agent.py`:

    for cell in sorted(env.fire):
        if cell not in known_fire and manhattan(agent position, cell) <= sensing_radius:
            known_fire.add(cell)
            new_fire.append(cell)

It returns the newly seen cells so the simulation can print them.
The default radius is 4 (`Simulation(env, sensing_radius=4)`). The menu does not expose it,
because the brief asked for no settings menu; it can be changed in code.

## Memory
Once a cell is in `known_fire` it stays there. The agent does not forget fire when it walks
away. Fire never goes out in this project, so this is always correct.

## Decisions
- Distance is `|row1 - row2| + |col1 - col2|`. Walls do not block sensing.
- Perception happens at the start of every step, before the agent decides.

## Edge cases
- Fire outside the radius is invisible, so the agent can walk toward it. It will see it
  when it gets within 4 cells and then replan.
- A fire that appears on the agent's own cell is not "perceived": the agent has already failed.

## Testing
`tests/test_agent.py` (TestAgentPerception): inside radius, outside radius, remembered after
moving away, already-known fire is not reported again.
