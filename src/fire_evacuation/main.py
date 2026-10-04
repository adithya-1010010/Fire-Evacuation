"""Terminal menu for the Fire Evacuation Agent."""

from .generator import random_environment, generate_environment, DIFFICULTIES, MIN_SIZE, MAX_SIZE
from .scenarios import SCENARIOS
from .simulation import Simulation, ESCAPED, cell_text, route_text

HELP_TEXT = """
A person (the agent) is inside a building and fire appears over time.
The agent must reach the exit using classical AI: rules + A* + replanning.

Symbols:  # wall   . floor   A agent   E exit   F fire   * planned route
Cells are written (row, column). Moves are up, down, left, right.

Each step the agent does:
  PERCEIVE  see fire within 4 cells (Manhattan distance) and remember it
  REASON    is my route still safe?
  DECIDE    keep going, or run A* again (replan)
  ACT       move one cell
Then the environment moves time forward and new fire may appear.

Menu:
  New Simulation   Random (program chooses size and difficulty) or
                   Custom (you choose rows, columns and difficulty)
  Preset Scenarios Three fixed demonstrations: replanning, multiple replanning, failure
"""


def ask_int(prompt, low, high):
    while True:
        text = input(prompt).strip()
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print(f"Please enter a number from {low} to {high}.")


def play(env):
    sim = Simulation(env)
    print(f"\nEnvironment: {env.name}   (fire events planned: "
          f"{sum(len(c) for c in env.fire_events.values())})")
    print(env.to_text())
    print("Symbols: # wall  . floor  A agent  E exit  F fire  * planned route\n")
    while sim.is_running():
        for line in sim.step():
            print(line)
        if sim.important:
            print(env.to_text(sim.agent.path))
            print(sim.status_text())
            print()
    print_report(sim)


def print_report(sim):
    """The end of the run: result, what happened, the route taken, the final map, metrics."""
    agent, env = sim.agent, sim.env
    walked = agent.walked
    escaped = sim.status == ESCAPED

    print("=" * 50)
    print("RESULT:", "AGENT ESCAPED!" if escaped else "AGENT FAILED")
    print("=" * 50)
    if escaped:
        print(f"The agent walked from {cell_text(walked[0])} to the exit {cell_text(walked[-1])} "
              f"in {sim.steps} steps with {agent.replans} replan(s).")
    else:
        print(f"The agent started at {cell_text(walked[0])} and stopped at {cell_text(walked[-1])} "
              f"after {sim.steps} steps. Reason: {sim.failure_reason}.")

    print("\nKey events (every step was printed above):")
    for kind, text in sim.events:
        print("  " + text)

    print(f"\nRoute the agent took ({sim.steps} moves):")
    for line in route_text(walked):
        print(line)

    start_row, start_col = walked[0]
    map_rows = env.to_text(walked).split("\n")
    map_rows[start_row] = map_rows[start_row][:start_col] + "S" + map_rows[start_row][start_col + 1:]
    if escaped:                                  # the agent is standing on the exit: show E
        row, col = env.exit_pos
        map_rows[row] = map_rows[row][:col] + "E" + map_rows[row][col + 1:]
    print("\nFinal map  (S start, * cells the agent walked, E exit, F fire"
          + ("):" if escaped else ", A where the agent stopped):"))
    print("\n".join(map_rows))

    print("\nMetrics:")
    for key, value in sim.get_metrics().items():
        print(f"  {key}: {value}")


def new_simulation_menu():
    while True:
        print("\n---------------- New Simulation ----------------\n")
        print("1. Random Environment")
        print("2. Custom Environment")
        print("3. Back")
        choice = ask_int("\nEnter your choice: ", 1, 3)
        if choice == 1:
            play(random_environment())
        elif choice == 2:
            print("\n---------------- Custom Environment ----------------\n")
            rows = ask_int(f"Rows ({MIN_SIZE}-{MAX_SIZE}): ", MIN_SIZE, MAX_SIZE)
            cols = ask_int(f"Columns ({MIN_SIZE}-{MAX_SIZE}): ", MIN_SIZE, MAX_SIZE)
            print("\nDifficulty:")
            names = list(DIFFICULTIES)
            for number, name in enumerate(names, 1):
                print(f"{number}. {name}")
            level = ask_int("\nEnter difficulty: ", 1, 3)
            play(generate_environment(rows, cols, names[level - 1]))
        else:
            return


def scenario_menu():
    while True:
        print("\n---------------- Preset Scenarios ----------------\n")
        print("1. Fire Blocks Route")
        print("2. Multiple Replanning")
        print("3. No Safe Route")
        print("4. Back")
        choice = ask_int("\nEnter your choice: ", 1, 4)
        if choice == 4:
            return
        play(SCENARIOS[choice - 1]())


def main():
    try:
        while True:
            print("\n" + "=" * 50)
            print("       INTELLIGENT FIRE EVACUATION AGENT")
            print("=" * 50 + "\n")
            print("1. New Simulation")
            print("2. Preset Scenarios")
            print("3. Help")
            print("4. Exit")
            choice = ask_int("\nEnter your choice: ", 1, 4)
            if choice == 1:
                new_simulation_menu()
            elif choice == 2:
                scenario_menu()
            elif choice == 3:
                print(HELP_TEXT)
            else:
                print("Goodbye.")
                return
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
